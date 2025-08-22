from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# ---------------------- Custom User Manager ----------------------
# A manager is like a "helper" that decides how new users are created.
# By default, Django expects a username field, but since we use email,
# we must define our own logic for creating users safely.
class UserManager(BaseUserManager):

    # Function to create a normal user
    def create_user(self, email, name, password=None, **extra_fields):
        # Ensure email is always provided (cannot be empty)
        if not email:
            raise ValueError('The Email field must be set')

        # Convert email to a standard lowercase format
        email = self.normalize_email(email)

        # Create a new user object (class is defined below) (not saved to DB yet)
        #  At this point, a User object is created in memory with email and name.  
        # The password is still None because we haven't set it yet. 
        user = self.model(email=email, name=name, **extra_fields)

        # Hash the password before storing it (important for security!)
        user.set_password(password)

        # Save the user into the database
        #  In PostgreSQL, for a customer, this will generate a query like:
        # INSERT INTO events_user (email, name, password, role, status, is_active, is_staff, created_at, updated_at)
        # VALUES ('customer@email.com', 'Alice', 'hashed_password', 'customer', 'active', true, false, NOW(), NOW())
        # RETURNING user_id;
        user.save(using=self._db)

        # Return the created user object
        return user

    # Function to create a superuser (admin with all permissions)
    def create_superuser(self, email, name, password=None, **extra_fields):
        # Set default role as 'admin'
        extra_fields.setdefault('role', 'admin')

        # Superusers must have access to Django admin
        extra_fields.setdefault('is_staff', True)

        # Superusers must have all permissions
        extra_fields.setdefault('is_superuser', True)

        # Reuse the normal user creation function with these extra fields
        # 👉 In PostgreSQL, for an admin, this will generate a query like:
        # INSERT INTO events_user (email, name, password, role, status, is_active, is_staff, is_superuser, created_at, updated_at)
        # VALUES ('admin@email.com', 'Bob', 'hashed_password', 'admin', 'active', true, true, true, NOW(), NOW())
        # RETURNING user_id;
        return self.create_user(email, name, password, **extra_fields)

    # Example: if you want to create an organizer manually (not superuser),
    # you can pass role='organizer' in extra_fields:
    # 👉 In PostgreSQL, this will generate:
    # INSERT INTO events_user (email, name, password, role, status, is_active, is_staff, created_at, updated_at)
    # VALUES ('organizer@email.com', 'Charlie', 'hashed_password', 'organizer', 'active', true, false, NOW(), NOW())
    # RETURNING user_id;

# ---------------------- User ----------------------
# The main User model — defines what fields and behavior a "user" has.
# Instead of Django's default username system, we are using email as the login field.
class User(AbstractBaseUser, PermissionsMixin):

    # Predefined choices for user roles
    ROLE_CHOICES = [
        ('admin', 'Admin'),          # system administrator
        ('organizer', 'Organizer'),  # event manager
        ('customer', 'Customer'),    # regular user buying tickets
    ]

    # Predefined choices for account status
    STATUS_CHOICES = [
        ('active', 'Active'),         # user can log in and use the system
        ('suspended', 'Suspended'),   # user is blocked
    ]

    # ---------------------- Database fields ----------------------

    user_id = models.AutoField(primary_key=True)  
    # Auto-incrementing unique ID for each user

    name = models.CharField(max_length=100)  
    # User's full name

    email = models.EmailField(unique=True, max_length=150)  
    # Email (must be unique, used for login)

    phone = models.CharField(max_length=20, blank=True, null=True)  
    # Optional phone number (blank in forms, null in DB)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)  
    # User role (must be one of ROLE_CHOICES)

    bio = models.TextField(blank=True, null=True)  
    # Optional short biography/about user

    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  
    # Optional profile picture, stored in 'media/profile_pics/'

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')  
    # Whether account is active or suspended (default: active)

    is_active = models.BooleanField(default=True)  
    # Required by Django auth system → False = cannot log in

    is_staff = models.BooleanField(default=False)  
    # Required by Django admin → True = user can access admin panel

    created_at = models.DateTimeField(auto_now_add=True)  
    # Auto-filled date when user is created

    updated_at = models.DateTimeField(auto_now=True)  
    # Auto-updated every time user info changes

    # ---------------------- Authentication settings ----------------------

    USERNAME_FIELD = 'email'  
    # Tells Django to use "email" as the unique login field (instead of username)

    REQUIRED_FIELDS = ['name']  
    # Extra fields required when creating a superuser (via CLI createsuperuser)

    # Attach the custom manager we created above
    objects = UserManager()

    # String representation (how user appears in admin or shell)
    def __str__(self):
        return f"{self.name} ({self.role})"

    # Extra metadata for this model
    class Meta:
        ordering = ['-created_at']         # Sort users by newest first
        verbose_name = 'user'              # Name shown in admin panel
        verbose_name_plural = 'users'      # Plural name shown in admin panel

# ---------------------- Venue Model ----------------------
# This model stores details of venues (places where events can be held)
# Each venue has a fixed name (from a list of famous places in Lahore),
# an address, and a seating capacity.
class Venue(models.Model):
    # ---------------------- Choice Field ----------------------
    # We define a list of 5 famous venues in Lahore.
    # Each item is a tuple (value, display name).
    # - 'value' is what gets saved in the database (short code).
    # - 'display name' is what shows in forms/admin/UI.
    VENUE_CHOICES = [
        ('pc', 'Pearl Continental Hotel'),
        ('falettis', 'Faletti’s Hotel'),
        ('alhamra', 'Alhamra Arts Council'),
        ('expo', 'Expo Center Lahore'),
        ('royalpalm', 'Royal Palm Golf & Country Club'),
    ]

    # ---------------------- Fields ----------------------
    # AutoField automatically generates a unique ID for each venue.
    venue_id = models.AutoField(primary_key=True)

    # Name of the venue (must be one of the 5 choices above).
    # max_length=50 means the database will allow up to 50 characters.
    name = models.CharField(max_length=50, choices=VENUE_CHOICES)

    # Address of the venue (e.g. street, area, etc.).
    # TextField is used for long text data (no max length limit).
    address = models.TextField()

    # How many people can the venue hold.
    # PositiveIntegerField only allows non-negative numbers.
    capacity = models.PositiveIntegerField()

    # ---------------------- String Representation ----------------------
    # This method controls how the venue object appears as a string.
    # get_name_display() automatically returns the human-readable name
    # from the VENUE_CHOICES (e.g. 'pc' → 'Pearl Continental Hotel').
    def __str__(self):
        return f"{self.get_name_display()} (Capacity: {self.capacity})"

# ---------------------- Event ----------------------
# This model represents an "Event" in the system.
# Example: a music concert, a sports match, a seminar, etc.
class Event(models.Model):

    # Predefined choices for event status.
    # Only one of these values can be stored in the "status" field.
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),     # Event is scheduled but not started yet
        ('ongoing', 'Ongoing'),       # Event is currently happening
        ('completed', 'Completed'),   # Event already finished
        ('cancelled', 'Cancelled'),   # Event has been cancelled
    ]

    # Predefined categories of events.
    CATEGORY_CHOICES = [
        ('music', 'Music'),           # Example: concerts, gigs
        ('sports', 'Sports'),         # Example: cricket, football, etc.
        ('education', 'Education'),   # Example: workshops, seminars
        ('technology', 'Technology'), # Example: hackathons, tech talks
        ('business', 'Business'),     # Example: conferences, trade shows
    ]

    # ---------------------- Database fields ----------------------

    event_id = models.AutoField(primary_key=True)  
    # Auto-generated unique ID for each event (1, 2, 3, …)

    title = models.CharField(max_length=200)  
    # Event title (e.g., "Lahore Music Fest 2025")

    description = models.TextField()  
    # Detailed description of the event

    organizer = models.ForeignKey(
        'User',                       # Linked to the User model (who is hosting the event)
        on_delete=models.CASCADE,     # If the organizer is deleted → delete their events too
        related_name='events'         # Allows reverse lookup: user.events.all()
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)  
    # Category of the event (must be one of CATEGORY_CHOICES)

    venue = models.ForeignKey(
        'Venue',                      # Linked to the Venue model
        on_delete=models.SET_NULL,    # If venue is deleted → keep event but set venue = NULL
        null=True,                    # Venue can be empty in DB
        blank=True                    # Venue can be left empty in forms
    )

    start_date = models.DateField()  
    # Date when the event starts

    start_time = models.TimeField()  
    # Time when the event starts

    end_date = models.DateField()  
    # Date when the event ends

    end_time = models.TimeField()  
    # Time when the event ends

    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    # Ticket price (e.g., 999.99). Default = free (0.00)

    capacity = models.PositiveIntegerField()  
    # How many people can attend (must be >= 0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'            # By default, every new event is "upcoming"
    )

    created_at = models.DateTimeField(auto_now_add=True)  
    # Auto-filled with the date/time when the event is first created

    updated_at = models.DateTimeField(auto_now=True)  
    # Auto-updated every time the event is edited

    # ---------------------- Utility Methods ----------------------

    def __str__(self):
        # Defines how an event is shown as text (e.g., in Django admin or shell)
        # Example: "Lahore Music Fest 2025 - Music (upcoming)"
        return f"{self.title} - {self.get_category_display()} ({self.status})"

    # ---------------------- Extra Configurations ----------------------

    class Meta:
        ordering = ['-start_date', '-start_time']  
        # Events will be ordered by latest start date/time first

        unique_together = ('title', 'start_date')  
        # Prevents duplicate event titles on the same date

# ---------------------- Booking ----------------------
class Booking(models.Model):
    # Choices for booking status (only these values will be allowed)
    STATUS_CHOICES = [
        ('pending', 'Pending'),       # Waiting for confirmation
        ('confirmed', 'Confirmed'),   # Successfully confirmed
        ('cancelled', 'Cancelled'),   # Booking cancelled
    ]

    # Primary key for each booking (unique ID auto-generated)
    booking_id = models.AutoField(primary_key=True)

    # Link booking to a Customer (User who books the event)
    # If a customer is deleted, their bookings are also deleted (CASCADE).
    # related_name = 'bookings' → we can access a user's bookings using user.bookings.all()
    customer = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Link booking to an Event
    # If the event is deleted, related bookings are deleted too.
    # related_name = 'bookings' → we can access event bookings using event.bookings.all()
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Number of tickets reserved by the customer for this event
    tickets_reserved = models.PositiveIntegerField()

    # Current booking status → must be one of STATUS_CHOICES
    # By default, it is set to 'pending'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Date & time when booking was created (set only once automatically)
    created_at = models.DateTimeField(auto_now_add=True)

    # Date & time when booking was last updated (auto-updates every time we save)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the booking object
    # Example: "Booking 1 - John Doe -> Music Concert (pending)"
    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer} -> {self.event.title} ({self.status})"

    class Meta:
        # Bookings will be ordered by 'created_at' in descending order (latest first)
        ordering = ['-created_at']

        # Prevents duplicate booking for the same customer & same event
        # Example: A customer cannot book the same event twice separately
        unique_together = ('customer', 'event')

# ---------------------- Payment ----------------------
class Payment(models.Model):
    # Available payment methods
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
    ]

    # Different statuses a payment can have
    STATUS_CHOICES = [
        ('pending', 'Pending'),      # Payment is created but not finished yet
        ('completed', 'Completed'),  # Payment was successful
        ('failed', 'Failed'),        # Payment attempt failed
        # Removed 'refunded' as you requested
    ]

    # Unique ID for each payment (auto-generated by Django)
    payment_id = models.AutoField(primary_key=True)

    # One-to-one relationship with Booking
    # (Each booking will have exactly one payment)
    booking = models.OneToOneField(
        'Booking',
        on_delete=models.CASCADE,    # If booking is deleted, delete payment too
        related_name='payment'       # Allows accessing payment from booking object
    )

    # The customer who made the payment
    customer = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,    # If customer is deleted, delete payment too
        related_name='payments'      # Allows accessing all payments from a user
    )

    # Payment method chosen by the customer
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)

    # Current status of the payment (default is "pending")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # The total amount paid
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # The date and time when payment was made
    payment_datetime = models.DateTimeField(auto_now_add=True)

    # String representation of the payment (for admin panel & debugging)
    def __str__(self):
        return f"Payment {self.payment_id} - {self.customer} ({self.status})"

# ---------------------- Review ----------------------
class Review(models.Model):
    # Each booking can have only one review
    booking = models.OneToOneField("Booking", on_delete=models.CASCADE, related_name="review")
    
    # The user who gave the review
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="reviews")
    
    # Rating between 1–5 stars
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  
    
    # Automatically set the date & time when review is created
    created_at = models.DateTimeField(auto_now_add=True)

    # Display review info as text
    def __str__(self):
        return f"Review by {self.user} - {self.rating} stars"

    class Meta:
        # A user can review a booking only once
        unique_together = ('user', 'booking')
