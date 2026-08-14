"""
accounts/utils.py
Email utility functions for VoteX.

Uses Brevo's HTTPS Transactional Email API.
No SMTP connection is required.
"""

import html
import requests

from django.conf import settings


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send_email(
    subject,
    message,
    recipient,
    fail_silently=False,
):
    """
    Send a transactional email through Brevo HTTPS API.

    Returns:
        True  -> email accepted by Brevo
        False -> email failed
    """

    if not recipient:
        return False

    api_key = getattr(settings, "BREVO_API_KEY", "")
    sender_email = getattr(settings, "BREVO_SENDER_EMAIL", "")
    sender_name = getattr(settings, "BREVO_SENDER_NAME", "VoteX")

    if not api_key:
        error = "BREVO_API_KEY is not configured"
        if fail_silently:
            return False
        raise RuntimeError(error)

    if not sender_email:
        error = "BREVO_SENDER_EMAIL is not configured"
        if fail_silently:
            return False
        raise RuntimeError(error)

    # Escape the plain-text message before putting it into HTML.
    safe_message = html.escape(message).replace("\n", "<br>")

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient,
            }
        ],
        "subject": subject,
        "textContent": message,
        "htmlContent": f"""
        <html>
        <body>
            <div style="
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #222;
                max-width: 650px;
                margin: auto;
            ">
                {safe_message}
            </div>
        </body>
        </html>
        """,
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        response = requests.post(
            BREVO_API_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )

        if response.status_code in (200, 201):
            return True

        error_message = (
            f"Brevo email failed. "
            f"HTTP {response.status_code}: {response.text}"
        )

        if fail_silently:
            return False

        raise RuntimeError(error_message)

    except requests.RequestException as exc:
        if fail_silently:
            return False

        raise RuntimeError(
            f"Could not connect to Brevo API: {exc}"
        ) from exc


def send_credentials_email(user, plain_password):
    """Send login credentials to a newly created student."""

    subject = "Your College Voting System Login Credentials"

    message = f"""
Dear {user.get_full_name() or user.username},

Your account has been created on the College Voting System.

Login Details:
--------------
Username : {user.username}
Password : {plain_password}

Login at:
https://votex-production-4825.up.railway.app/accounts/login/

Please change your password after first login.

If you did not request this account, please contact the administration.

Best regards,
College Election Committee
""".strip()

    return _send_email(
        subject=subject,
        message=message,
        recipient=user.email,
        fail_silently=False,
    )


def send_vote_confirmation_email(user, election):
    """Send confirmation after a student successfully votes."""

    subject = f"Vote Confirmation - {election.name}"

    message = f"""
Dear {user.get_full_name() or user.username},

You have successfully cast your vote in {election.name}.

Election Details:
----------------
Election : {election.name}
Voted at : {election.start_time.strftime('%d %B %Y')}

Your vote has been recorded securely.
Thank you for participating!

Results will be published after the election ends on
{election.end_time.strftime('%d %B %Y, %I:%M %p')}.

Best regards,
College Election Committee
""".strip()

    return _send_email(
        subject=subject,
        message=message,
        recipient=user.email,
        fail_silently=True,
    )


def send_election_scheduled_email(users, election):
    """Notify assigned students when an election is scheduled."""

    subject = f"Election Announcement: {election.name}"

    results = []

    for user in users:
        if not user.email:
            continue

        message = f"""
Dear {user.get_full_name() or user.username},

You have been registered to vote in the upcoming election!

Election Details:
-----------------
Election  : {election.name}
Starts    : {election.start_time.strftime('%d %B %Y, %I:%M %p')}
Ends      : {election.end_time.strftime('%d %B %Y, %I:%M %p')}
Description: {election.description or 'N/A'}

Your Login Credentials:
-----------------------
Username : {user.username}
Password : [Your registered password]

If you have forgotten your password, please use the
"Forgot Password" link on the login page.

Login:
https://votex-production-4825.up.railway.app/accounts/login/

Best regards,
College Election Committee
""".strip()

        results.append(
            _send_email(
                subject=subject,
                message=message,
                recipient=user.email,
                fail_silently=True,
            )
        )

    return all(results) if results else False


def send_voting_reminder_email(users, election):
    """Send a reminder before voting opens."""

    subject = f"Reminder: Voting Opens Soon - {election.name}"

    results = []

    for user in users:
        if not user.email:
            continue

        message = f"""
Dear {user.get_full_name() or user.username},

This is a gentle reminder that voting for "{election.name}"
opens in less than 2 hours!

Election Details:
-----------------
Election  : {election.name}
Opens at  : {election.start_time.strftime('%d %B %Y, %I:%M %p')}
Closes at : {election.end_time.strftime('%d %B %Y, %I:%M %p')}

Please make sure to cast your vote on time.
Every vote counts!

Login:
https://votex-production-4825.up.railway.app/accounts/login/

Best regards,
College Election Committee
""".strip()

        results.append(
            _send_email(
                subject=subject,
                message=message,
                recipient=user.email,
                fail_silently=True,
            )
        )

    return all(results) if results else False


def send_vote_otp_email(user, election, otp):
    """Send OTP required to verify a vote."""

    if not user.email:
        return False

    subject = f"Vote Verification OTP - {election.name}"

    message = f"""
Dear {user.get_full_name() or user.username},

You are attempting to cast your vote in "{election.name}".

Your OTP code is:

{otp}

Please enter this code to verify and submit your vote.

Do not share this code with anyone.

Best regards,
College Election Committee
""".strip()

    return _send_email(
        subject=subject,
        message=message,
        recipient=user.email,
        fail_silently=False,
    )


def send_results_published_email(users, election):
    """Notify students that election results are available."""

    subject = f"Results Published: {election.name}"

    results = []

    for user in users:
        if not user.email:
            continue

        message = f"""
Dear {user.get_full_name() or user.username},

The results for "{election.name}" have just been made public!

You can now log in to the portal and view the detailed
outcome of the election.

View Results:
https://votex-production-4825.up.railway.app/voting/results/{election.id}/

Best regards,
College Election Committee
""".strip()

        results.append(
            _send_email(
                subject=subject,
                message=message,
                recipient=user.email,
                fail_silently=True,
            )
        )

    return all(results) if results else False


def send_password_reset_otp_email(user, otp):
    """Send OTP for password reset."""

    if not user.email:
        return False

    subject = "Password Reset Request - VoteX"

    message = f"""
Dear {user.get_full_name() or user.username},

You have requested to reset your password for the
College Voting System (VoteX).

Your Password Reset OTP is:

{otp}

This code is valid for 10 minutes.

If you did not request this, please ignore this email
and ensure your account is secure.

Best regards,
College Election Committee
""".strip()

    return _send_email(
        subject=subject,
        message=message,
        recipient=user.email,
        fail_silently=False,
    )