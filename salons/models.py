from django.db import models
from django.conf import settings
from users.models import User
from django.utils import timezone

class Salon(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Roles.ADMIN},
        related_name='salon',
        help_text="User with role=ADMIN who owns this salon"
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)
    stylists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='salons',
        limit_choices_to={'role': User.Roles.STYLIST},
        help_text="Approved stylists working at this salon"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='services',
        help_text="Salon offering this service"
    )
    name = models.CharField(max_length=100)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.duration}m) - {self.price} AED"
    
    


class Availability(models.Model):
    """
    Defines a stylist's available time window on a given weekday.
    """
    stylist   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'STYLIST'},
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    weekday   = models.PositiveSmallIntegerField(
        choices=[(i, day) for i, day in enumerate(
            ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        )],
        help_text="0=Monday, 6=Sunday"
    )
    start_time = models.TimeField()
    end_time   = models.TimeField()

    class Meta:
        unique_together = ('stylist', 'weekday', 'start_time')

    def __str__(self):
        return f"{self.stylist.username}: {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING',   'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELED',  'Canceled'),
    ]

    customer    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        limit_choices_to={'role': User.Roles.CUSTOMER}
    )
    salon       = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    stylist     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stylist_bookings',
        limit_choices_to={'role': User.Roles.STYLIST}
    )
    service     = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('stylist', 'start_time')

    def save(self, *args, **kwargs):
        # Auto-calculate end_time based on service duration if not provided
        if not self.end_time:
            self.end_time = self.start_time + timezone.timedelta(minutes=self.service.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.username} @ {self.start_time} with {self.stylist.username}"
