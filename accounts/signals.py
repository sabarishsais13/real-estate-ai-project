from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Profile


@receiver(post_migrate)
def create_missing_profiles(sender, **kwargs):
    User = get_user_model()
    for user in User.objects.all().only("id"):
        Profile.objects.get_or_create(user=user)
