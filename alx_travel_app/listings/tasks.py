from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation_email(email, first_name, booking_id, amount):
    print(f"Sending payment confirmation email to {email} for booking {booking_id} of amount {amount}")
    subject = "Payment Confirmation - ALX Travel App"
    message = f"Hi {first_name},\n\nYour payment for booking {booking_id} of amount {amount} has been confirmed.\n\nThank you for using our service!"
    send_mail(subject, message, "noreply@alxtravel.com", [email])

@shared_task
def send_booking_confirmation_email(recipient_email, booking_details):
    subject = 'Booking Confirmation'
    message = f"Dear customer,\n\nYour booking details:\n{booking_details}\n\nThank you for choosing us!"
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        from_email,
        [recipient_email],
        fail_silently=False,
    )
    return f"Confirmation email sent to {recipient_email}"

