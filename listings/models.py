from django.db import models
from django.conf import settings

class Property(models.Model):

    PROPERTY_TYPES = [
        ('Apartment',         'Apartment'),
        ('Villa',             'Villa'),
        ('Independent House', 'Independent House'),
        ('Plot',              'Plot'),
        ('Studio',            'Studio'),
        ('Penthouse',         'Penthouse'),
    ]

    BHK_CHOICES = [
        ('Studio', 'Studio'),
        ('1 BHK',  '1 BHK'),
        ('2 BHK',  '2 BHK'),
        ('3 BHK',  '3 BHK'),
        ('4 BHK',  '4 BHK'),
        ('5 BHK',  '5 BHK'),
        ('Plot',   'Plot'),
    ]

    # Model Fields - matching EXACT naming convention from requirements
    # id is automatically added by Django (models.AutoField)
    title         = models.CharField(max_length=200)
    location      = models.CharField(max_length=200)
    price         = models.CharField(max_length=50) # Keep as string for display like $12,500,000
    price_value   = models.FloatField(default=0)    # Helpful for filtering
    bhk           = models.CharField(max_length=20, choices=BHK_CHOICES)
    type          = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    area          = models.CharField(max_length=50)
    floor         = models.CharField(max_length=20)
    facing        = models.CharField(max_length=50, blank=True, null=True)
    description   = models.TextField(blank=True, null=True)
    amenities     = models.TextField(blank=True, null=True)
    image         = models.ImageField(upload_to='property_images/', blank=True, null=True)
    
    # 360 viewer assets (stores base64 data URLs)
    living_room_360 = models.TextField(blank=True, null=True)
    kitchen_360     = models.TextField(blank=True, null=True)
    bedroom_360     = models.TextField(blank=True, null=True)
    bathroom_360    = models.TextField(blank=True, null=True)

    # Extra functional fields
    city          = models.CharField(max_length=100, blank=True, null=True)
    badge         = models.CharField(max_length=20, blank=True, null=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    owner         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="listed_properties",
        null=True,
        blank=True,
    )
    views_count   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.title} - {self.location} - {self.price}"


class PropertyInteraction(models.Model):
    VIEW = "view"
    CLICK = "click"
    SUBMIT = "submit"
    SAVE = "save"

    INTERACTION_CHOICES = [
        (VIEW, "View"),
        (CLICK, "Click"),
        (SUBMIT, "Submit"),
        (SAVE, "Save"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="property_interactions",
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="interactions",
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} {self.interaction_type} {self.property_id}"
