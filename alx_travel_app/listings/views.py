from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer

import requests, environ, json, uuid 
from pathlib import Path
from django.urls import reverse

from .tasks import send_payment_confirmation_email, send_booking_confirmation_email
# Initialize environment variables
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(env_file=str(BASE_DIR) + '/.env')    

# SECURITY WARNING: keep the secret key used in production secret!
CHAPA_SECRET_KEY = env('CHAPA_SECRET_KEY')

class ListingView(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Listing instances.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned listings to those created by the authenticated user.
        """
        user = self.request.user
        if user.is_authenticated:
            return Listing.objects.filter(host=user).order_by('-created_at')
        return Listing.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingView(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Booking instances.
    Only returns bookings made by the currently authenticated user.
    """
    serializer_class = BookingSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """
        Create a new booking and initiate payment.
        This method expects the request data to contain the necessary booking details.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(user=request.user)

        # ✅ Define user_email and booking_details here
        user_email = request.user.email
        booking_details = (
            f"Booking ID: {booking.booking_id}\n"
            f"Property: {booking.listing.name}\n"
            f"Location: {booking.listing.location}\n"
            f"Start Date: {booking.start_date}\n"
            f"End Date: {booking.end_date}\n"
            f"Total Price: {booking.total_price}\n"
            f"Status: {booking.status}"
        )

        # ✅ Trigger Celery email task
        send_booking_confirmation_email.delay(recipient_email=user_email, booking_details=booking_details)

        # Call initiate-payment with booking_id
        try:
            url = self.request.build_absolute_uri(
                reverse('payment-initiate-transaction')
            )
            payload = {
                "booking_id": str(booking.booking_id)
            }

            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            payment_response = response.json()
            checkout_url = payment_response.get("checkout_url")
        except Exception as e:
            checkout_url = None
            print("Error initiating payment:", e)

        headers = self.get_success_headers(serializer.data)

        return Response({
            "booking": serializer.data,
            "checkout_url": checkout_url
        }, status=status.HTTP_201_CREATED, headers=headers)

class PaymentView(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Payment instances.
    Only returns payments related to bookings made by the currently authenticated user.
    """
    serializer_class = PaymentSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = []

    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='initiate-payment', permission_classes=[])
    def initiate_transaction(self, request):
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({"error": "booking_id is required"}, status=400)

        booking = Booking.objects.filter(booking_id=booking_id).first()
        if not booking:
            return Response({"error": "Invalid booking ID"}, status=404)

        tx_ref = f"TX-{uuid.uuid4()}"
        payload = {
            "amount": str(booking.total_price),
            "currency": "USD",
            "tx_ref": tx_ref,
            # "return_url": "https://yourfrontend.com/payment/success",
            **({"first_name": booking.user.first_name} if booking.user.first_name else {}),
            **({"last_name": booking.user.last_name} if booking.user.last_name else {}),
            "email": booking.user.email,
            "phone_number": "08012345678",  # TODO: get from profile if needed
            "callback_url": "http://localhost:8000/api/payment/verify-payment"
        }

        headers = {
            'Authorization': f"Bearer {CHAPA_SECRET_KEY}",
            'Content-Type': 'application/json',
        }

        try:
            chapa_response = requests.post(
                "https://api.chapa.co/v1/transaction/initialize",
                json=payload,
                headers=headers
            )
            data = chapa_response.json()

            if chapa_response.status_code == 200 and data.get("status") == "success":
                Payment.objects.create(
                    amount=booking.total_price,
                    status="Pending",
                    transaction_id=tx_ref,
                    booking=booking
                )
                return Response({
                    "checkout_url": data['data']['checkout_url'],
                    "tx_ref": tx_ref,
                    "message": "Payment initiated"
                })

            return Response({"error": "Failed to initiate Chapa payment", "chapa": data}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['get'], url_path='verify-payment', permission_classes=[])
    def verify_transaction(self, request):
        """
        Verify transaction through chapa payment gateway
        """
        try:
            param = request.GET
            trx_ref = param.get('trx_ref')

            if trx_ref is None:
                return Response({"error": "trx_ref is required"}, status=400)

            url = f"https://api.chapa.co/v1/transaction/verify/{trx_ref}"
            headers = {
                'Authorization': f"Bearer {CHAPA_SECRET_KEY}",
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers)
            data = response.json()
            print(f"Chapa verification response for trx_ref={trx_ref}: {json.dumps(data, indent=2)} (HTTP {response.status_code})")

            payment = Payment.objects.filter(transaction_id=trx_ref).first()
            if response.status_code == 200 and data.get("status") == "success":
                status = data['data']['status']  # typically 'success' or 'failed'

                if payment:
                    payment.status = 'Completed' if status == 'success' else 'Failed'
                    payment.save()

                # Optionally send confirmation email
                send_payment_confirmation_email.delay(
                    email=payment.booking.user.email,
                    first_name=payment.booking.user.first_name,
                    booking_id=str(payment.booking.booking_id),
                    amount=str(payment.amount)
                )

                return Response({
                    "message": "Payment verified",
                    "status": status,
                    "trx_ref": trx_ref
                })
            
            # ✅ For non-200 responses or failed verification
            if payment:
                payment.status = 'Failed'
                payment.save()

            return Response({"error": "Verification failed"}, status=400)
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return Response({"error": "Failed to verify payment"}, status=500)