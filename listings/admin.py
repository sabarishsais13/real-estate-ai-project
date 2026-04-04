from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display   = ['title', 'city', 'price', 'price_value',
                      'bhk', 'type', 'badge', 'is_active']
    list_filter    = ['city', 'type', 'bhk', 'badge', 'is_active']
    search_fields  = ['title', 'location', 'city']
    list_editable  = ['is_active']
    ordering       = ['-created_at']
    readonly_fields = ['created_at']
