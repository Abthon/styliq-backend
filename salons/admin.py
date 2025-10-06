from django.contrib import admin
from .models import Salon

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name','owner','is_approved','created_at')
