from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
import requests
import json
import os
from django.conf import settings

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PaymentView(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Payment instances.
    Only returns payments related to bookings made by the currently authenticated user.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='initiate-payment')
    def initiate_transaction(self, request):
        """
        Initiate payment with chapa payment gateway
        """
        body=request.data
        amount = data.get('amount')


        url = "https://api.chapa.co/v1/transaction/initialize"
        payload = {
            "amount": amount,
            "phone_number": "0912345678",
            "tx_ref": "chewatatest-6669",
            "callback_url": "https://webhook.site/077164d6-29cb-40df-ba29-8a00e59a7e60",
            # "return_url": "https://www.google.com/",
        }
        headers = {
            'Authorization': f"Bearer {getattr(settings, 'CHAPA_API_KEY', '')}",
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.text
        print(data)
        return Response(data)