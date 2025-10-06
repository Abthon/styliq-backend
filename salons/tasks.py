from celery import shared_task
from twilio.rest import Client
from django.conf import settings
import logging
from .models import Booking



logger = logging.getLogger(__name__)
@shared_task
def send_booking_confirmation(booking_id):
    booking = Booking.objects.get(pk=booking_id)
    # Prepare message
    msg = (
        f"Hi {booking.customer.first_name}, your booking at "
        f"{booking.start_time.strftime('%Y-%m-%d %H:%M')} "
        f"with {booking.stylist.first_name} is confirmed."
    )
    if settings.DEBUG:
        logger.info(f"[DEV] Booking confirmation message: {msg}")
    else:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=msg,
            from_=settings.TWILIO_FROM_NUMBER,
            to=booking.customer.username
        )
