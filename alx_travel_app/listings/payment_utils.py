# listings/payment_utils.py

import requests, uuid
from .models import Payment
from django.conf import settings

CHAPA_SECRET_KEY = settings.CHAPA_SECRET_KEY

def initiate_chapa_payment(booking):
    tx_ref = f"TX-{uuid.uuid4()}"

    payload = {
        "amount": str(booking.total_price),
        "currency": "USD",
        "tx_ref": tx_ref,
        # "return_url": "https://yourfrontend.com/payment/success",
        "first_name": booking.user.first_name,
        "last_name": booking.user.last_name,
        "email": booking.user.email,
        "phone_number": booking.user.phone_number,  # or from profile
        "callback_url": "http://localhost:8000/api/payment/verify-payment"
    }

    headers = {
        'Authorization': f'Bearer {CHAPA_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("status") == "success":
        Payment.objects.create(
            amount=booking.total_price,
            status="Pending",
            transaction_id=tx_ref,
            booking=booking
        )
        return {
            "checkout_url": data['data']['checkout_url'],
            "tx_ref": tx_ref,
            "message": "Payment initiated"
        }

    raise Exception(f"Payment initiation failed: {data}")



# @action(detail=False, methods=['post'], url_path='initiate-payment', permission_classes=[])
# def initiate_transaction(self, request):
#     """
#     Initiate payment with chapa payment gateway
#     """
#     try:
#         body=request.data
#         amount = body.get('amount')
#         phone_number = body.get('phone_number')
#         booking_id = body.get('booking_id')

#         if not all([amount, phone_number]):
#             return Response({"error": "Missing required fields"}, status=400)
        
#         booking = Booking.objects.filter(id=booking_id).first()
#         if not booking:
#             return Response({"error": "Invalid booking ID"}, status=404)

#         print(f"Initiating payment of {amount} with Chapa")
#         print(f"Request Body {json.dumps(request.data)}")

#         url = "https://api.chapa.co/v1/transaction/initialize"
#         payload = {
#             "amount": amount,
#             "phone_number": phone_number,
#         }

#         # Optionally add optional fields if present in request data
#         optional_fields = ["currency", "email", "first_name", "last_name", "return_url", "customization", "trx_ref", "callback_url"]
#         for field in optional_fields:
#             value = body.get(field)
#             if value is not None:
#                 payload[field] = value

#         headers = {
#             'Authorization': f"Bearer {CHAPA_SECRET_KEY}",
#             'Content-Type': 'application/json'
#         }

#         print(f"CHAPA_SECRET_KEY  {CHAPA_SECRET_KEY}")

#         response = requests.post(url, json=payload, headers=headers)
#         data = response.json()

#         print(data)
#         if response.status_code == 200 and data.get("status") == "success":
#             trx_ref = data['data']['trx_ref']
#             checkout_url = data['data'].get('checkout_url')

#             Payment.objects.create(
#                 amount=amount,
#                 status="Pending",
#                 transaction_id=trx_ref,
#                 booking=booking
#             )
#             return Response({
#                 "checkout_url": checkout_url,
#                 "trx_ref": trx_ref,
#                 "message": "Payment initiated successfully"
#             })

#         return Response({"error": "Failed to initiate payment"}, status=500)
#     except Exception as e:
#         print(f"Error initiating payment: {e}")
#         return Response({"error": "Failed to initiate payment"}, status=500)
