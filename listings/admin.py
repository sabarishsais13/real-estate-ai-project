from django.contrib import admin
from .models import Property, PropertyInteraction

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display   = ['title', 'city', 'price', 'price_value',
                      'bhk', 'type', 'badge', 'views_count', 'owner', 'is_active']
    list_filter    = ['city', 'type', 'bhk', 'badge', 'is_active']
    search_fields  = ['title', 'location', 'city']
    list_editable  = ['is_active']
    ordering       = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(PropertyInteraction)
class PropertyInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "property", "interaction_type", "created_at")
    list_filter = ("interaction_type", "created_at")
    search_fields = ("user__username", "property__title")
