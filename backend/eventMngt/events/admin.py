# Import Django admin (this is the tool that lets us manage models in the Django admin panel)
from django.contrib import admin

# Import all our models so we can register them in admin
from .models import User, Venue, Event, Booking, Payment, Review


# ---------------------- User Admin ----------------------
# This class customizes how the User model will appear in the admin panel.
# @admin.register(User) means we are telling Django:
# "Hey, register this model with the admin panel using the UserAdmin class"
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # list_display → columns to show in the admin list view for users
    list_display = ('name', 'email', 'role', 'status', 'is_staff', 'created_at')

    # list_filter → filters shown on the right-hand sidebar in admin
    list_filter = ('role', 'status', 'is_staff', 'is_active')

    # search_fields → enables search bar functionality on these fields
    search_fields = ('name', 'email', 'phone')

    # ordering → default order of users in the list (here newest first, because of "-created_at")
    ordering = ('-created_at',)


# ---------------------- Venue Admin ----------------------
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    # Show venue name, address, and capacity in the admin list
    list_display = ('name', 'address', 'capacity')

    # Add filter by venue name
    list_filter = ('name',)

    # Enable search on address
    search_fields = ('address',)


# ---------------------- Event Admin ----------------------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # Show important details about each event in admin list
    list_display = ('title', 'organizer', 'category', 'venue', 'start_date', 'end_date', 'status')

    # Allow filtering by category, status, and venue
    list_filter = ('category', 'status', 'venue')

    # Enable search for event title, description, and organizer's name
    # Note: "organizer__name" means we search inside the related User model's "name" field
    search_fields = ('title', 'description', 'organizer__name')

    # Default order: latest events first (by start_date)
    ordering = ('-start_date',)


# ---------------------- Booking Admin ----------------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Show booking details in the admin list
    list_display = ('booking_id', 'customer', 'event', 'tickets_reserved', 'status', 'created_at')

    # Allow filtering by booking status and event
    list_filter = ('status', 'event')

    # Enable search by customer name and event title
    search_fields = ('customer__name', 'event__title')

    # Show latest bookings first
    ordering = ('-created_at',)


# ---------------------- Payment Admin ----------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Show key payment details in the admin list
    list_display = ('payment_id', 'customer', 'booking', 'method', 'status', 'amount', 'payment_datetime')

    # Allow filtering by payment status and method
    list_filter = ('status', 'method')

    # Enable search by customer name and related event title
    search_fields = ('customer__name', 'booking__event__title')

    # Order payments by newest first
    ordering = ('-payment_datetime',)


# ---------------------- Review Admin ----------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # Show who reviewed, which booking, rating, and when it was created
    list_display = ('user', 'booking', 'rating', 'created_at')

    # Allow filtering by rating
    list_filter = ('rating',)

    # Enable search by reviewer's name and booking's event title
    search_fields = ('user__name', 'booking__event__title')

    # Show latest reviews first
    ordering = ('-created_at',)
