from django.contrib import admin
from .models import Profile, SavedProperty


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "updated_at")
    search_fields = ("user__username", "user__email", "full_name", "phone")


@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ("user", "property", "created_at")
    search_fields = ("user__username", "property__title", "property__location")
