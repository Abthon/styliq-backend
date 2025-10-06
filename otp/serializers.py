from rest_framework import serializers
from django.utils.crypto import get_random_string
from .models import OTP
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from salons.models import Salon

# ---- Customer Serializers ----
class CustomerRequestOTPSerializer(serializers.Serializer):
    phone     = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=150)

    def validate(self, data):
        # Unique phone
        if User.objects.filter(username=data['phone']).exists():
            raise serializers.ValidationError("Phone number already registered.")
        # E.164 format
        phone = data['phone']
        if not phone.startswith('+') or not phone[1:].isdigit():
            raise serializers.ValidationError(
                "Phone must be in E.164 format, e.g. +971501234567"
            )
        return data

    def create(self, validated_data):
        # Create inactive user
        user = User.objects.create_user(
            username=validated_data['phone'],
            first_name=validated_data['full_name'],
            role=User.Roles.CUSTOMER,
            is_active=False,
            is_approved=False,
            password=get_random_string(12)
        )
        # Create OTP record
        return OTP.objects.create(user=user)

class CustomerVerifyOTPSerializer(serializers.Serializer):
    reference = serializers.UUIDField()
    code      = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            otp = OTP.objects.get(id=data['reference'], salon__isnull=True)
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid reference.")
        if otp.is_verified:
            raise serializers.ValidationError("OTP already verified.")
        if otp.code != data['code']:
            otp.attempts += 1; otp.save()
            if otp.attempts >= 3:
                otp.user.delete(); otp.delete()
                raise serializers.ValidationError(
                    "Too many incorrect attempts; registration canceled."
                )
            raise serializers.ValidationError(
                f"Incorrect code, {3 - otp.attempts} attempts left."
            )
        data['otp_obj'] = otp
        return data

    def create(self, validated_data):
        otp = validated_data.pop('otp_obj')
        user = otp.user
        # Activate user
        user.is_active = True; user.is_approved = True; user.save()
        otp.is_verified = True; otp.save()
        # Issue tokens
        refresh = RefreshToken.for_user(user)
        return {
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user': { 'username': user.username, 'first_name': user.first_name }
        }

# ---- Stylist Serializers ----
class StylistRequestOTPSerializer(serializers.Serializer):
    phone     = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=150)
    salon_id  = serializers.IntegerField()

    def validate(self, data):
        # Unique phone
        if User.objects.filter(username=data['phone']).exists():
            raise serializers.ValidationError("Phone number already registered.")
        # E.164 format
        if not data['phone'].startswith('+'):
            raise serializers.ValidationError("Phone must be in E.164 format.")
        # Check salon exists & approved
        try:
            salon = Salon.objects.get(id=data['salon_id'], is_approved=True)
        except Salon.DoesNotExist:
            raise serializers.ValidationError("Salon not found or not approved.")
        data['salon'] = salon
        return data

    def create(self, validated_data):
        salon = validated_data.pop('salon')
        user = User.objects.create_user(
            username=validated_data['phone'],
            first_name=validated_data['full_name'],
            role=User.Roles.STYLIST,
            is_active=False,
            is_approved=False,
            password=get_random_string(12)
        )
        otp = OTP.objects.create(user=user, salon=salon)
        return otp

class StylistVerifyOTPSerializer(serializers.Serializer):
    reference = serializers.UUIDField()
    code      = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            otp = OTP.objects.get(id=data['reference'], salon__isnull=False)
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid reference.")
        if otp.is_verified:
            raise serializers.ValidationError("OTP already verified.")
        if otp.code != data['code']:
            otp.attempts += 1; otp.save()
            if otp.attempts >= 3:
                otp.user.delete(); otp.delete()
                raise serializers.ValidationError(
                    "Too many incorrect attempts; registration canceled."
                )
            raise serializers.ValidationError(
                f"Incorrect code, {3 - otp.attempts} attempts left."
            )
        data['otp_obj'] = otp
        return data

    def create(self, validated_data):
        otp = validated_data.pop('otp_obj')
        user = otp.user
        salon = otp.salon
        # Activate stylist and link to salon
        user.is_active = True; user.is_approved = True; user.save()
        salon.stylists.add(user)
        otp.is_verified = True; otp.save()
        # Issue tokens
        refresh = RefreshToken.for_user(user)
        return {
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user': { 'username': user.username, 'first_name': user.first_name }
        }

class SalonSignupSerializer(serializers.Serializer):
    """
    Sign up a new salon-admin and create their Salon profile.
    """
    phone      = serializers.CharField(max_length=20)
    email      = serializers.EmailField()
    password   = serializers.CharField(write_only=True)
    salon_name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        # 1) Create the User with role=ADMIN
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['salon_name'],  # temporarily store salon name
            role=User.Roles.ADMIN,
            is_active=True,
            is_approved=False,  # await manual approval
        )

        # 2) Create the Salon and link to this user
        Salon.objects.create(
            owner=user,
            name=validated_data['salon_name'],
            phone=validated_data['phone'],
            is_approved=False,
        )

        return user