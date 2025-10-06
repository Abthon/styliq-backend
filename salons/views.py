from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Salon, Service, User, Availability, Booking
from .serializers import SalonSerializer, ServiceSerializer, SalonListSerializer, AvailabilitySerializer, BookingSerializer
from users.permissions import IsSalonAdmin, IsStylist, IsCustomer
from rest_framework.exceptions import ValidationError
from .tasks import send_booking_confirmation

class SalonViewSet(viewsets.ModelViewSet):
    serializer_class = SalonSerializer
    permission_classes = [IsAuthenticated, IsSalonAdmin]
    lookup_field = 'pk'
    lookup_value_regex = '[0-9]+'  # ensure integer ID

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Roles.ADMIN:
            return Salon.objects.filter(owner=user)
        return Salon.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.owner != self.request.user:
            raise PermissionDenied("You do not own this salon.")
        serializer.save()

class ServiceViewSet(viewsets.ModelViewSet):
    """
    CRUD for services. Restricted to the salon owner: only they can manage services for their salon.
    """
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsSalonAdmin]
    lookup_field = 'pk'
    lookup_value_regex = '[0-9]+'

    def get_queryset(self):
        # Only return services for the salon owned by the current user
        user = self.request.user
        return Service.objects.filter(salon__owner=user)

    def perform_create(self, serializer):
        # Attach the salon based on current user
        try:
            salon = Salon.objects.get(owner=self.request.user)
        except Salon.DoesNotExist:
            raise PermissionDenied("Salon not found for current user.")
        serializer.save(salon=salon)

    def perform_update(self, serializer):
        # Ensure the service belongs to this user's salon
        if serializer.instance.salon.owner != self.request.user:
            raise PermissionDenied("You do not own this service.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure the service belongs to this user's salon
        if instance.salon.owner != self.request.user:
            raise PermissionDenied("You do not own this service.")
        instance.delete()
        
class SalonPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public endpoints for listing and retrieving approved salons.
    """
    queryset = Salon.objects.filter(is_approved=True)
    serializer_class = SalonListSerializer
    permission_classes = [AllowAny]
    
    
class AvailabilityViewSet(viewsets.ModelViewSet):
    """
    Stylists manage their weekly availability slots.
    """
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated, IsStylist]  # reuse or create IsStylist permission
    lookup_field        = 'pk'                  # ← add this
    lookup_value_regex  = '[0-9]+'  

    def get_queryset(self):
        # Only availabilities belonging to the current stylist
        return Availability.objects.filter(stylist=self.request.user)

    def perform_create(self, serializer):
        serializer.save(stylist=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.stylist != self.request.user:
            raise PermissionDenied("Cannot modify another stylist's availability.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.stylist != self.request.user:
            raise PermissionDenied("Cannot delete another stylist's availability.")
        instance.delete()
        
        

class BookingViewSet(viewsets.ModelViewSet):
    """
    Customers create bookings; both parties can list or cancel.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field        = 'pk'                  # ← add here
    lookup_value_regex  = '[0-9]+'              # ← add here

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Roles.CUSTOMER:
            return Booking.objects.filter(customer=user)
        if user.role == User.Roles.STYLIST:
            return Booking.objects.filter(stylist=user)
        if user.role == User.Roles.ADMIN:
            # salon admins see bookings for their salon
            salon = Salon.objects.get(owner=user)
            return Booking.objects.filter(salon=salon)
        return Booking.objects.none()

    def perform_create(self, serializer):
        
        user = self.request.user
        if user.role != User.Roles.CUSTOMER:
            raise ValidationError("Only customers can create bookings.")
        # Prevent double booking
        start = serializer.validated_data['start_time']
        stylist = serializer.validated_data['stylist']
        if Booking.objects.filter(stylist=stylist, start_time=start).exists():
            raise ValidationError("This time slot is already booked.")
        # Attach customer & salon automatically
        salon = serializer.validated_data['stylist'].salons.get(pk=serializer.validated_data['salon'].pk)
        booking = serializer.save(customer=user, salon=salon)
        send_booking_confirmation.delay(booking.id)
        # serializer.save(customer=user, salon=salon)
