from rest_framework import serializers
from .models import Salon, Service, Availability, Booking
from users.serializers import UserSerializer

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'duration', 'price']
        extra_kwargs = {
            'name': {'required': True},
            'duration': {'required': True},
            'price': {'required': True}
        }
        
class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'weekday', 'start_time', 'end_time']

class SalonSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    stylists = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Salon
        fields = ['id', 'owner', 'name', 'phone', 'is_approved', 'stylists', 'services']
        read_only_fields = ['is_approved', 'owner', 'stylists', 'services']
        
class SalonListSerializer(serializers.ModelSerializer):
    services      = ServiceSerializer(many=True, read_only=True)
    stylist_count = serializers.IntegerField(source='stylists.count', read_only=True)

    class Meta:
        model = Salon
        fields = ['id', 'name', 'phone', 'services', 'stylist_count']
        

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'salon', 'stylist',
            'service', 'start_time', 'end_time', 'status'
        ]
        read_only_fields = ['customer', 'end_time', 'status']
