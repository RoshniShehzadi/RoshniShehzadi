# Import serializers module from Django REST Framework.
# Serializers are used to convert complex data (like Django models)
# into JSON format so it can be sent in an API response,
# and also to convert incoming JSON data from the frontend
# into model objects that can be saved in the database.
from rest_framework import serializers  
from .models import User

# Import the Event model that we want to serialize.
from .models import Event  
# Importing our Venue model (the table in the database we want to work with)
from .models import Venue

# Import the Booking model from the current app's models.py file.
# This is the model we want to convert into JSON or receive data for.
from .models import Booking

from django.contrib.auth import authenticate
 # Used to check user credentials (email & password)

# -------------------- Registration Serializer --------------------
# A serializer is used to convert data between JSON (from frontend) and Python objects (in Django).
# This serializer will handle registration of new users.
class RegisterSerializer(serializers.ModelSerializer):
    # Password should not be returned to frontend, so we mark it as write_only
    password = serializers.CharField(write_only=True)

    class Meta:
        # This serializer is linked with the User model
        model = User
        # These are the fields we expect when a new user registers
        fields = ['name', 'email', 'password', 'role']

    # This method tells Django how to create a new user with the given data
    def create(self, validated_data):
        # Use the built-in create_user method (handles password hashing automatically)
        user = User.objects.create_user(
            email=validated_data['email'],   # Take email from input data
            name=validated_data['name'],     # Take name from input data
            password=validated_data['password'], # Hash and save password securely
            role=validated_data['role']      # Save user role (like admin, organizer, etc.)
        )
        return user   # Return the newly created user object


# -------------------- Login Serializer --------------------
# This serializer will handle the login process.
class LoginSerializer(serializers.Serializer):
    # User will provide these two fields for login
    email = serializers.EmailField()                # Email must be in correct format
    password = serializers.CharField(write_only=True) # Password will not be shared back

    # This method checks if the provided email & password are correct
    def validate(self, data):
        # Authenticate checks the user credentials with the database
        user = authenticate(email=data['email'], password=data['password'])

        # If authentication fails (no user found with these credentials)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        # If the user exists but their status is not active
        if user.status != 'active':
            raise serializers.ValidationError("Your account is suspended")

        # If everything is fine, add user object to data and return it
        data['user'] = user
        return data



# Define a serializer class for the Event model.
# A serializer works like a "translator" between the Django model and JSON.
# It works in BOTH directions:
# 1️⃣ Model object → JSON: used when sending data to frontend (GET requests)
# 2️⃣ JSON → Model object: used when receiving data from frontend to create/update events (POST/PUT/PATCH requests)
class EventSerializer(serializers.ModelSerializer):  
    # The Meta class gives extra information to the serializer.
    class Meta:
        # Tell the serializer which model it is connected to.
        # In this case, we are connecting it with our Event model.
        model = Event  

        # Define which fields should be included when converting the Event object to JSON
        # or when creating/updating an Event object from JSON.
        # "__all__" means "include all fields from the Event model"
        # Example: if Event has fields like title, description, date, location,
        # then all of them will be included automatically.
        fields = '__all__'  

# Serializer: helps convert complex Python objects (like Django models) 
# into simple data formats (like JSON) that can be sent through APIs.
# It also validates incoming data before saving it to the database.
class VenueSerializer(serializers.ModelSerializer):
    # Meta class gives extra information to the serializer
    class Meta:
        model = Venue       # Tell serializer to use the Venue model
        fields = '__all__'  # Include ALL fields from the Venue model in the API
                            # (e.g., name, location, capacity, etc.)

# Create a serializer class for the Booking model.
# This will allow us to easily send and receive Booking data through APIs.
class BookingSerializer(serializers.ModelSerializer):
    # The Meta class tells the serializer which model to use
    # and what fields of that model should be included.
    class Meta:
        model = Booking       # Link this serializer to the Booking model
        fields = '__all__'    # Include ALL fields from the Booking model in the API