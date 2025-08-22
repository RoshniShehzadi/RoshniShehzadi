
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer
from .models import Booking
from .serializers import BookingSerializer
# Importing our app-specific files
from .models import Venue                           # The Venue model (represents a table in the database)
from .serializers import VenueSerializer            # Serializer (converts Python objects <-> JSON)

# Import serializers that handle validation and conversion between JSON and Python objects
from .serializers import RegisterSerializer, LoginSerializer

# Import Django functions to manage user sessions
from django.contrib.auth import login, logout



# -------------------- Register Endpoint --------------------
# This function handles user registration (creating a new user)
# It accepts only POST requests from the client (React form)
@api_view(['POST'])
def register_view(request):
    # Deserialize the incoming JSON data using RegisterSerializer
    # This will check if required fields (name, email, password, role) are present
    serializer = RegisterSerializer(data=request.data)

    # If the data is valid according to the serializer rules
    if serializer.is_valid():
        # Save the new user to the database
        user = serializer.save()

        # Return a success response with user info (but not password!)
        return Response({
            "message": f"{user.role.capitalize()} registered successfully!",  # Friendly message
            "user": {
                "id": user.user_id,    # Unique ID of the user
                "name": user.name,     # User's full name
                "email": user.email,   # User's email
                "role": user.role      # Role of the user (admin/organizer/customer)
            }
        }, status=status.HTTP_201_CREATED)  # HTTP 201 = resource created

    # If the data is invalid, return errors with HTTP 400 (bad request)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Login Endpoint --------------------
# This function handles user login
# Only POST requests allowed (React form sends email & password)
@api_view(['POST'])
def login_view(request):
    # Deserialize the incoming login data (email & password)
    serializer = LoginSerializer(data=request.data)

    # If data is valid and credentials are correct
    if serializer.is_valid():
        # Get the authenticated user object from the validated data
        user = serializer.validated_data['user']

        # Log the user in using Django's session framework
        # This creates a session cookie that keeps the user logged in
        login(request, user)

        # Return success response with user details (excluding password)
        return Response({
            "message": f"{user.role.capitalize()} logged in successfully!",  # Friendly message
            "user": {
                "id": user.user_id,    # Unique ID of the user
                "name": user.name,     # Full name
                "email": user.email,   # Email used to login
                "role": user.role      # User role
            }
        }, status=status.HTTP_200_OK)  # HTTP 200 = OK

    # If login fails (wrong credentials or suspended account), return errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- Logout Endpoint --------------------
# This function handles logging out a user
# It destroys the user's session so they are no longer authenticated
@api_view(['POST'])
def logout_view(request):
    # Use Django logout function to remove session data
    logout(request)

    # Return a simple success message
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)



# ---------------------- CREATE EVENT ----------------------
@api_view(['POST'])  # Only allow POST requests
def create_event(request):
    # Step 1: Pass incoming JSON data (from React form) into EventSerializer
    serializer = EventSerializer(data=request.data)  
    
    # Step 2: Validate the data (check required fields, field types, etc.)
    if serializer.is_valid():
        # Step 3: If valid, save the data into the Event table
        serializer.save()
        # Step 4: Return the created event data with HTTP 201 (Created)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Step 5: If invalid, return error messages with HTTP 400 (Bad Request)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------- READ ALL EVENTS ----------------------
@api_view(['GET'])  # Only allow GET requests
def get_events(request):
    # Fetch all events from the Event table
    events = Event.objects.all()
    
    # Convert queryset into JSON using serializer (many=True for multiple records)
    serializer = EventSerializer(events, many=True)
    
    # Return the list of all events
    return Response(serializer.data)


# ---------------------- READ SINGLE EVENT ----------------------
@api_view(['GET'])  # Only allow GET requests
def get_event(request, pk):
    try:
        # Try to find the event with given primary key (id)
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        # If not found, return error response
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    # If found, serialize the event into JSON
    serializer = EventSerializer(event)
    return Response(serializer.data)


# ---------------------- UPDATE EVENT (FULL) ----------------------
@api_view(['PUT'])  # Full update (all fields must be provided)
def update_event(request, pk):
    try:
        # Get the event that needs to be updated
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    # Pass existing event + new data into serializer (replaces old values)
    serializer = EventSerializer(event, data=request.data)  
    if serializer.is_valid():
        serializer.save()  # Save updated values
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------- UPDATE EVENT (PARTIAL) ----------------------
@api_view(['PATCH'])  # Partial update (only some fields can be provided)
def partial_update_event(request, pk):
    try:
        # Get the event
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    # Use partial=True so only given fields will be updated
    serializer = EventSerializer(event, data=request.data, partial=True)  
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------- DELETE EVENT ----------------------
@api_view(['DELETE'])  # Only allow DELETE requests
def delete_event(request, pk):
    try:
        # Get the event to delete
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    # Delete the event from database
    event.delete()
    return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

#----------------------- Venue CRUD Operations ----------------------


# ---------------- CREATE VENUE ----------------
@api_view(['POST'])  # This endpoint will accept only POST requests
def create_venue(request):
    # Create a serializer object with the data sent by the user in the request
    serializer = VenueSerializer(data=request.data)
    
    # Check if the data is valid according to the serializer's rules
    if serializer.is_valid():
        serializer.save()  # Save the data in the database (creates a new Venue record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Send back the created data with status 201 (Created)
    
    # If invalid, send error messages with status 400 (Bad Request)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- READ VENUES ----------------
@api_view(['GET'])  # This endpoint will accept only GET requests
def get_venues(request):
    # Fetch all Venue records from the database
    venues = Venue.objects.all()
    
    # Convert the Venue objects into JSON format using the serializer
    serializer = VenueSerializer(venues, many=True)  # many=True because there can be multiple records
    
    # Send the list of venues back to the client
    return Response(serializer.data)


# ---------------- PARTIAL UPDATE VENUE ----------------
@api_view(['PATCH'])  # This endpoint will accept only PATCH requests (partial updates)
def partial_update_venue(request, pk):
    try:
        # Try to find the venue by its primary key (pk)
        venue = Venue.objects.get(pk=pk)
    except Venue.DoesNotExist:
        # If not found, return a 404 (Not Found) error
        return Response({"error": "Venue not found"}, status=status.HTTP_404_NOT_FOUND)

    # Pass both the existing venue and new data (partial=True means only some fields can be updated)
    serializer = VenueSerializer(venue, data=request.data, partial=True)
    
    # If new data is valid, update and save changes
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)  # Send back the updated venue
    
    # If invalid, send error messages
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- DELETE VENUE ----------------
@api_view(['DELETE'])  # This endpoint will accept only DELETE requests
def delete_venue(request, pk):
    try:
        # Try to find the venue by its primary key (pk)
        venue = Venue.objects.get(pk=pk)
    except Venue.DoesNotExist:
        # If not found, return a 404 (Not Found) error
        return Response({"error": "Venue not found"}, status=status.HTTP_404_NOT_FOUND)

    # Delete the venue from the database
    venue.delete()
    
    # Send confirmation message with status 204 (No Content → successful deletion)
    return Response({"message": "Venue deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

#----------------------- Booking CRUD Operations ----------------------
# ---------------------- CREATE BOOKING ----------------------
@api_view(['POST'])
def create_booking(request):
    # Take JSON data from frontend and convert it to a Booking object
    serializer = BookingSerializer(data=request.data)
    
    # Check if the data is valid according to BookingSerializer
    if serializer.is_valid():
        serializer.save()  # Save into PostgreSQL database
        # PostgreSQL query generated by Django (example):
        # INSERT INTO events_booking (customer_id, event_id, tickets_reserved, status, created_at, updated_at)
        # VALUES (1, 2, 3, 'pending', NOW(), NOW()) RETURNING booking_id;
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Return validation errors if data is invalid
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------- GET ALL BOOKINGS ----------------------
@api_view(['GET'])
def get_all_bookings(request):
    user = request.user  # Current logged-in user

    # Admin: can see all bookings
    if user.role == 'admin':
        bookings = Booking.objects.all()
        # PostgreSQL query:
        # SELECT * FROM events_booking;

    # Organizer: can see bookings only for their events
    elif user.role == 'organizer':
        bookings = Booking.objects.filter(event__organizer=user)
        # PostgreSQL query:
        # SELECT * FROM events_booking
        # JOIN events_event ON events_booking.event_id = events_event.event_id
        # WHERE events_event.organizer_id = <user_id>;

    # Customer: can see only their own bookings
    else:
        bookings = Booking.objects.filter(customer=user)
        # PostgreSQL query:
        # SELECT * FROM events_booking WHERE customer_id = <user_id>;

    # Convert Booking objects to JSON to send to frontend
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
