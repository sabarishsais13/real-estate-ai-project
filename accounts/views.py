from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from listings.models import Property, PropertyInteraction

from .forms import LoginForm, ProfileUpdateForm, SignUpForm, UserUpdateForm
from .models import Profile, SavedProperty


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False # Deactivate until email verification
        user.save()
        
        # Send Verification Email
        current_site = get_current_site(request)
        mail_subject = "Verify your GRIHA account"
        message = render_to_string("accounts/verification_email.html", {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        })
        to_email = form.cleaned_data.get("email")
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.content_subtype = "html"
        email.send()
        
        return render(request, "accounts/verification_sent.html", {"email": to_email})
        
    return render(request, "accounts/signup.html", {"form": form})


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for confirming your email. You can now login.")
        return redirect("login")
    else:
        return render(request, "accounts/verification_failed.html")


def resend_verification_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email__iexact=email)
            if user.is_active:
                messages.info(request, "Account is already active. Please login.")
                return redirect("login")
            
            # Resend Verification Email
            current_site = get_current_site(request)
            mail_subject = "Verify your GRIHA account"
            message = render_to_string("accounts/verification_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })
            email_msg = EmailMessage(mail_subject, message, to=[email])
            email_msg.content_subtype = "html"
            email_msg.send()
            return render(request, "accounts/verification_sent.html", {"email": email})
        except User.DoesNotExist:
            # For security, we don't say explicitly that it failed, just show the sent page.
            # But let's add an error message
            messages.error(request, "No account found with this email.")
            return redirect("resend_verification")
            
    return render(request, "accounts/resend_verification.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if not form.cleaned_data.get("remember_me"):
            request.session.set_expiry(0)
        messages.success(request, "Welcome back.")
        return redirect("dashboard")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard_view(request):
    listed_properties = request.user.listed_properties.order_by("-created_at")
    interacted_property_ids = (
        PropertyInteraction.objects.filter(user=request.user)
        .values_list("property_id", flat=True)
        .distinct()
    )
    interacted_properties = Property.objects.filter(id__in=interacted_property_ids).order_by("-created_at")
    saved_items = request.user.saved_properties.select_related("property").order_by("-created_at")
    last_viewed = (
        PropertyInteraction.objects.filter(user=request.user, interaction_type=PropertyInteraction.VIEW)
        .select_related("property")
        .order_by("-created_at")[:5]
    )
    context = {
        "listed_properties": listed_properties,
        "interacted_properties": interacted_properties,
        "saved_items": saved_items,
        "last_viewed": last_viewed,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def toggle_saved_property(request, property_id):
    prop = get_object_or_404(Property, id=property_id, is_active=True)
    saved = SavedProperty.objects.filter(user=request.user, property=prop)

    if saved.exists():
        saved.delete()
        messages.info(request, "Property removed from saved list.")
    else:
        SavedProperty.objects.create(user=request.user, property=prop)
        PropertyInteraction.objects.create(
            user=request.user,
            property=prop,
            interaction_type=PropertyInteraction.SAVE,
        )
        messages.success(request, "Property saved.")

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))
