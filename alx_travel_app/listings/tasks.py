from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_payment_confirmation_email(email, first_name, booking_id, amount):
    print(f"Sending payment confirmation email to {email} for booking {booking_id} of amount {amount}")
    subject = "Payment Confirmation - ALX Travel App"
    message = f"Hi {first_name},\n\nYour payment for booking {booking_id} of amount {amount} has been confirmed.\n\nThank you for using our service!"
    send_mail(subject, message, "noreply@alxtravel.com", [email])
