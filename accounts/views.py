"""
accounts/views.py
Login, logout, and role-based redirect views.
Google OAuth is handled by social_django automatically.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


import random
from .models import CustomUser, PasswordResetOTP
from .utils import (
    send_password_reset_otp_email,
    send_signup_otp_email,
)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Unified login page supporting username/password and Google OAuth.
    Handles google_error query param set by social-auth on AuthForbidden.
    """
    if request.user.is_authenticated:
        return redirect('accounts:redirect')

    # Handle Google OAuth error redirect (set via SOCIAL_AUTH_LOGIN_ERROR_URL)
    google_error = request.GET.get('google_error')
    if google_error == 'not_registered':
        messages.error(
            request,
            '⚠️ Your Google account is not registered in this system. '
            'Please use the credentials provided by your administrator.'
        )

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('accounts:redirect')
            else:
                messages.error(request, 'Your account is disabled. Contact admin.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    """Step 1: Request email and send OTP."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, 'accounts/forgot_password.html')
            
        user = CustomUser.objects.filter(email=email).first()
        if user:
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(user=user, otp=otp)
            
            # Send Email
            if send_password_reset_otp_email(user, otp):
                request.session['reset_email'] = email
                messages.success(request, f"A 6-digit OTP has been sent to {email}.")
                return redirect('accounts:verify_password_otp')
            else:
                messages.error(request, "Failed to send OTP email. Please try again later.")
        else:
            # For security, don't reveal if user exists. 
            # But in this context (college), it's probably fine to be direct.
            messages.error(request, "No account found with that email address.")
            
    return render(request, 'accounts/forgot_password.html')


@require_http_methods(["GET", "POST"])
def verify_password_otp(request):
    """Step 2: Verify the OTP sent to email."""
    email = request.session.get('reset_email')
    if not email:
        return redirect('accounts:forgot_password')
        
    if request.method == 'POST':
        otp_code = request.POST.get('otp', '').strip()
        user = get_object_or_404(CustomUser, email=email)
        
        # Check latest non-expired, non-verified OTP
        otp_record = PasswordResetOTP.objects.filter(
            user=user, 
            otp=otp_code, 
            is_verified=False
        ).first()
        
        if otp_record and not otp_record.is_expired:
            otp_record.is_verified = True
            otp_record.save()
            request.session['otp_verified'] = True
            messages.success(request, "OTP verified successfully. You can now set a new password.")
            return redirect('accounts:reset_password')
        else:
            messages.error(request, "Invalid or expired OTP code.")
            
    return render(request, 'accounts/verify_password_otp.html', {'email': email})


@require_http_methods(["GET", "POST"])
def reset_password(request):
    """Step 3: Set a new password."""
    email = request.session.get('reset_email')
    is_verified = request.session.get('otp_verified')
    
    if not email or not is_verified:
        messages.error(request, "Session expired or unauthorized. Please start again.")
        return redirect('accounts:forgot_password')
        
    if request.method == 'POST':
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_password')
        
        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
        elif len(pass1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        else:
            user = get_object_or_404(CustomUser, email=email)
            user.set_password(pass1)
            user.save()
            
            # Clear session
            del request.session['reset_email']
            del request.session['otp_verified']
            
            messages.success(request, "Your password has been reset successfully. Please login with your new password.")
            return redirect('accounts:login')
            
    return render(request, 'accounts/reset_password.html')


@login_required
def redirect_view(request):
    """
    Redirect user to appropriate dashboard based on role.
    Called after both traditional login and Google OAuth login.
    """
    user = request.user
    if user.is_superuser or user.role == 'django_admin':
        return redirect('/django-admin/')
    elif user.role == 'web_admin':
        return redirect('web_admin:dashboard')
    else:
        # Default: student dashboard
        return redirect('voting:student_dashboard')


def logout_view(request):
    """Log out and redirect to home."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import IntegrityError

from .models import SignupOTP
from .utils import send_signup_otp_email


COLLEGE_EMAIL_DOMAIN = getattr(
    settings,
    'COLLEGE_EMAIL_DOMAIN',
    'rajalakshmi.edu.in'
).lower().lstrip('@')


def _valid_college_email(email):
    """Return True only for an email belonging to the configured college domain."""
    try:
        validate_email(email)
    except ValidationError:
        return False

    return email.lower().endswith('@' + COLLEGE_EMAIL_DOMAIN)


@require_http_methods(["GET", "POST"])
def signup(request):
    """Step 1: collect student details and send a college-email OTP."""

    if request.user.is_authenticated:
        return redirect('accounts:redirect')

    if request.method == 'POST':

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        student_id = request.POST.get('student_id', '').strip()
        department = request.POST.get('department', '').strip()
        phone = request.POST.get('phone', '').strip()

        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Required fields
        if not first_name or not email or not student_id or not password:
            messages.error(
                request,
                'Please fill in all required fields.'
            )

        # College email validation
        elif not _valid_college_email(email):
            messages.error(
                request,
                f'Please use your college email ending with '
                f'@{COLLEGE_EMAIL_DOMAIN}.'
            )

        # Password validation
        elif password != confirm_password:
            messages.error(
                request,
                'Passwords do not match.'
            )

        elif len(password) < 8:
            messages.error(
                request,
                'Password must be at least 8 characters long.'
            )

        # Duplicate email
        elif CustomUser.objects.filter(
            email__iexact=email
        ).exists():
            messages.error(
                request,
                'An account with this email already exists. Please log in instead.'
            )

        # Duplicate student ID
        elif CustomUser.objects.filter(
            student_id__iexact=student_id
        ).exists():
            messages.error(
                request,
                'This student ID is already registered.'
            )

        else:
            # Generate OTP
            otp = str(random.randint(100000, 999999))

            # Remove previous unfinished signup
            SignupOTP.objects.filter(
                email__iexact=email,
                is_verified=False
            ).delete()

            # Store only hashed password
            signup_record = SignupOTP.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                department=department,
                phone=phone,
                password_hash=make_password(password),
                otp=otp,
            )

            try:
                send_signup_otp_email(email, otp)

                request.session['signup_email'] = email

                messages.success(
                    request,
                    f'Verification OTP sent to {email}.'
                )

                return redirect(
                    'accounts:verify_signup_otp'
                )

            except Exception as exc:

                signup_record.delete()

                messages.error(
                    request,
                    'Unable to send verification email. '
                    'Please try again.'
                )

    return render(
        request,
        'accounts/signup.html',
        {
            'college_domain': COLLEGE_EMAIL_DOMAIN,
        }
    )


@require_http_methods(["GET", "POST"])
def verify_signup_otp(request):
    """Step 2: verify college email OTP and create student account."""

    email = request.session.get('signup_email')

    if not email:
        return redirect('accounts:signup')

    if request.method == 'POST':

        otp_code = request.POST.get('otp', '').strip()

        record = SignupOTP.objects.filter(
            email__iexact=email,
            otp=otp_code,
            is_verified=False,
        ).first()

        if not record or record.is_expired:

            messages.error(
                request,
                'Invalid or expired OTP code.'
            )

        else:

            # Check email again
            if CustomUser.objects.filter(
                email__iexact=record.email
            ).exists():

                messages.error(
                    request,
                    'An account with this email already exists. Please log in.'
                )

                record.delete()
                request.session.pop('signup_email', None)

                return redirect('accounts:login')

            # Check student ID again
            if CustomUser.objects.filter(
                student_id__iexact=record.student_id
            ).exists():

                messages.error(
                    request,
                    'This student ID is already registered.'
                )

                record.delete()
                request.session.pop('signup_email', None)

                return redirect('accounts:login')

            # Generate username
            username = f"stu_{record.student_id.lower()}"

            if CustomUser.objects.filter(
                username__iexact=username
            ).exists():

                messages.error(
                    request,
                    'This student ID is already associated with an account.'
                )

                record.delete()
                request.session.pop('signup_email', None)

                return redirect('accounts:login')

            try:

                user = CustomUser.objects.create(
                    username=username,
                    email=record.email,
                    first_name=record.first_name,
                    last_name=record.last_name,
                    role='student',
                    student_id=record.student_id,
                    department=record.department or None,
                    phone=record.phone or None,

                    # Password is already hashed
                    password=record.password_hash,

                    is_active=True,
                )

            except IntegrityError:

                messages.error(
                    request,
                    'This student information is already registered.'
                )

                return redirect('accounts:signup')

            # Mark verified and remove temporary record
            record.is_verified = True
            record.save(update_fields=['is_verified'])
            record.delete()

            request.session.pop('signup_email', None)

            messages.success(
                request,
                f'Account created successfully. '
                f'Your username is {user.username}. Please log in.'
            )

            return redirect('accounts:login')

    return render(
        request,
        'accounts/verify_signup_otp.html',
        {
            'email': email
        }
    )