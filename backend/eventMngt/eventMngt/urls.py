"""
URL configuration for eventMngt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from events import views   # correct import from the app
 # Import all functions from views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    # ---------------- Auth Routes ----------------
    path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),

    # ---------------- Event Routes ----------------
    path('events/', views.get_events, name='get_events'),                     # GET all events
    path('events/my/', views.get_my_events, name='get_my_events'),            # GET events for logged-in organizer
    path('events/<int:pk>/', views.get_events, name='get_event'),             # GET single event (if needed)
    path('events/create/', views.create_event, name='create_event'),          # POST new event
    path('events/update/<int:pk>/', views.update_event, name='update_event'), # PUT full update
    path('events/partial/<int:pk>/', views.partial_update_event, name='partial_update_event'),  # PATCH partial update
    path('events/delete/<int:pk>/', views.delete_event, name='delete_event'), # DELETE event

    # ---------------- Venue Routes ----------------
    path('venues/', views.get_venues, name='get_venues'),                     # GET all venues
    path('venues/create/', views.create_venue, name='create_venue'),          # POST new venue
    path('venues/partial/<int:pk>/', views.partial_update_venue, name='partial_update_venue'),  # PATCH partial update
    path('venues/delete/<int:pk>/', views.delete_venue, name='delete_venue'), # DELETE venue

    # ---------------- Booking Routes ----------------
    path('bookings/', views.get_all_bookings, name='get_all_bookings'),       # GET all bookings for user
    path('bookings/create/', views.create_booking, name='create_booking'),    # POST new booking
    path('bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),  # POST cancel booking
]