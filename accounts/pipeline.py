"""
accounts/pipeline.py
Custom social-auth pipeline steps for VoteX.
"""
from social_core.exceptions import AuthForbidden


def require_pre_registration(backend, details, user=None, *args, **kwargs):
    """
    Match Google login to an existing VoteX account using its dedicated
    ``google_email`` field.

    For backwards compatibility, an existing student's current ``email``
    may be used once; it is then copied into ``google_email``. This allows
    existing accounts to migrate without breaking their first Google login.

    Google must never be allowed to create an arbitrary new voting account.
    """
    if user:
        return

    email = (details.get('email') or '').lower().strip()
    if not email:
        raise AuthForbidden(backend)

    from accounts.models import CustomUser

    # Preferred identity: dedicated Google email.
    existing_user = CustomUser.objects.filter(google_email__iexact=email).first()
    if existing_user:
        return {'user': existing_user}

    # Backwards-compatible migration for accounts created before google_email.
    # Only students are eligible for this automatic migration.
    existing_user = CustomUser.objects.filter(
        email__iexact=email,
        role='student',
    ).first()

    if existing_user:
        existing_user.google_email = email
        existing_user.save(update_fields=['google_email'])
        return {'user': existing_user}

    raise AuthForbidden(backend)


def set_google_email(backend, details, user=None, *args, **kwargs):
    """
    Persist the Google account email without changing the user's normal
    email, username, first name, or last name.
    """
    if not user:
        return

    email = (details.get('email') or '').lower().strip()
    if not email:
        return

    if user.google_email != email:
        user.google_email = email
        user.save(update_fields=['google_email'])


def set_student_role(backend, user, response, *args, **kwargs):
    """Ensure OAuth users have the student role when no role is set."""
    if user and not user.role:
        user.role = 'student'
        user.save(update_fields=['role'])
