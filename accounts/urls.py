from django.urls import path

from . import views

urlpatterns = [
    path("accounts/signup/", views.signup_view, name="signup"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/dashboard/", views.dashboard_view, name="dashboard"),
    path("accounts/profile/", views.profile_view, name="profile"),
    path("accounts/saved/<int:property_id>/toggle/", views.toggle_saved_property, name="toggle_saved_property"),
]
