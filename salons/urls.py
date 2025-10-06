from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalonViewSet, ServiceViewSet, SalonPublicViewSet, AvailabilityViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'salons',        SalonViewSet,       basename='salon-admin')
router.register(r'services',      ServiceViewSet,     basename='service')
router.register(r'public-salons', SalonPublicViewSet, basename='salon-public')
router.register(r'availabilities', AvailabilityViewSet, basename='availability')
router.register(r'bookings', BookingViewSet, basename='booking')



urlpatterns = [
    path('', include(router.urls)),
]
