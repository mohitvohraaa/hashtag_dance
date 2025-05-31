from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'seats', 'booking_date')
    list_filter = ('event', 'booking_date')
    search_fields = ('user__username', 'event__title', 'seats')
    ordering = ('-booking_date',)
    date_hierarchy = 'booking_date'
