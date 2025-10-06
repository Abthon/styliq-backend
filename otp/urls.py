# back-end/otp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerAuthViewSet, StylistAuthViewSet, SalonSignupViewSet

router = DefaultRouter()
router.register(r'customers', CustomerAuthViewSet, basename='customer-auth')
router.register(r'stylists',  StylistAuthViewSet,  basename='stylist-auth')
router.register(r'salon-signup', SalonSignupViewSet, basename='salon-signup')

urlpatterns = [
    path('', include(router.urls)),
]

