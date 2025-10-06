from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging
from .models import OTP
from .serializers import (
    CustomerRequestOTPSerializer, CustomerVerifyOTPSerializer,
    StylistRequestOTPSerializer, StylistVerifyOTPSerializer,
    SalonSignupSerializer
)
from django.conf import settings

logger = logging.getLogger(__name__)

class CustomerAuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def get_serializer_class(self):
        if self.action == 'request_otp': return CustomerRequestOTPSerializer
        if self.action == 'verify_otp':  return CustomerVerifyOTPSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], url_path='request-otp')
    def request_otp(self, request):
        ser = self.get_serializer(data=request.data); ser.is_valid(raise_exception=True)
        otp = ser.save()
        if settings.DEBUG:
            logger.info(f"[DEV] Customer OTP code={otp.code}, ref={otp.id}")
        return Response({'reference': str(otp.id)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        ser = self.get_serializer(data=request.data); ser.is_valid(raise_exception=True)
        tokens = ser.save()
        return Response(tokens, status=status.HTTP_200_OK)

class StylistAuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def get_serializer_class(self):
        if self.action == 'request_otp': return StylistRequestOTPSerializer
        if self.action == 'verify_otp':  return StylistVerifyOTPSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], url_path='request-otp')
    def request_otp(self, request):
        ser = self.get_serializer(data=request.data); ser.is_valid(raise_exception=True)
        otp = ser.save()
        if settings.DEBUG:
            logger.info(f"[DEV] Stylist OTP code={otp.code}, ref={otp.id}")
        return Response({'reference': str(otp.id)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        ser = self.get_serializer(data=request.data); ser.is_valid(raise_exception=True)
        tokens = ser.save()
        return Response(tokens, status=status.HTTP_200_OK)
    
    
class SalonSignupViewSet(viewsets.GenericViewSet):
        
    permission_classes = [AllowAny]
    serializer_class  = SalonSignupSerializer
    
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Signup successful. Awaiting admin approval."},
            status=status.HTTP_201_CREATED
        )