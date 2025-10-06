import random
import uuid
from django.db import models
from django.conf import settings

class OTP(models.Model):
    """
    One-time passcode for registration flows.
    Supports both customers and stylists.
    """
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user          = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp',
        help_text='Linked inactive user awaiting verification'
    )
    salon         = models.ForeignKey(
        'salons.Salon',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Optional salon for stylist registrations'
    )
    code          = models.CharField(max_length=6)
    attempts      = models.PositiveSmallIntegerField(default=0)
    is_verified   = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_code():
        return f"{random.randint(0, 999999):06d}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)