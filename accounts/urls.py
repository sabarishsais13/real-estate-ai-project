from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("accounts/signup/", views.signup_view, name="signup"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/dashboard/", views.dashboard_view, name="dashboard"),
    path("accounts/profile/", views.profile_view, name="profile"),
    path("accounts/saved/<int:property_id>/toggle/", views.toggle_saved_property, name="toggle_saved_property"),
    
    # Email Verification
    path("accounts/activate/<uidb64>/<token>/", views.activate_view, name="activate"),
    path("accounts/resend-verification/", views.resend_verification_email, name="resend_verification"),

    # Password Reset
    path("accounts/password-reset/", 
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset_form.html"), 
         name="password_reset"),
    path("accounts/password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), 
         name="password_reset_done"),
    path("accounts/password-reset-confirm/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), 
         name="password_reset_confirm"),
    path("accounts/password-reset-complete/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), 
         name="password_reset_complete"),
]
