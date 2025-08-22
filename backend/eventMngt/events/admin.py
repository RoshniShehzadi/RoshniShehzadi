from django.contrib import admin
from .models import User, Venue, Event, Booking, Payment, Review

# ---------------------- User Admin ----------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'status', 'is_staff', 'created_at')
    list_filter = ('role', 'status', 'is_staff', 'is_active')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-created_at',)

# ---------------------- Venue Admin ----------------------
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity')
    list_filter = ('name',)
    search_fields = ('address',)

# ---------------------- Event Admin ----------------------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'venue', 'start_date', 'end_date', 'status')
    list_filter = ('category', 'status', 'venue')
    search_fields = ('title', 'description', 'organizer__name')
    ordering = ('-start_date',)

# ---------------------- Booking Admin ----------------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer', 'event', 'tickets_reserved', 'status', 'created_at')
    list_filter = ('status', 'event')
    search_fields = ('customer__name', 'event__title')
    ordering = ('-created_at',)

# ---------------------- Payment Admin ----------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'customer', 'booking', 'method', 'status', 'amount', 'payment_datetime')
    list_filter = ('status', 'method')
    search_fields = ('customer__name', 'booking__event__title')
    ordering = ('-payment_datetime',)

# ---------------------- Review Admin ----------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__name', 'booking__event__title')
    ordering = ('-created_at',)
