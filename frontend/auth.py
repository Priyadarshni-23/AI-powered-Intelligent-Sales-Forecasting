import re
import requests

API_BASE = "http://127.0.0.1:8000"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Friendlier, field-specific messages for the FastAPI/Pydantic error codes
# we're most likely to see from /auth/signup, keyed by (field, error type).
_FIELD_ERROR_MESSAGES = {
    ("email", "value_error"): "Please enter a valid email address, like name@example.com.",
    ("username", "string_too_short"): "Username must be at least 3 characters.",
    ("password", "string_too_short"): "Password must be at least 6 characters.",
}


def _friendly_field_name(loc):
    """Turn a Pydantic error 'loc' path like ['body', 'email'] into 'Email'."""
    field = loc[-1] if loc else "field"
    return str(field).replace("_", " ").capitalize()


def _humanize_validation_errors(detail):
    """
    FastAPI returns 422 errors as a list of dicts, e.g.
    [{'type': 'value_error', 'loc': ['body', 'email'], 'msg': '...', ...}]
    Turn that into short, readable, user-facing sentences instead of
    dumping the raw list.
    """
    if isinstance(detail, str):
        return detail

    if isinstance(detail, list):
        messages = []
        for err in detail:
            if not isinstance(err, dict):
                messages.append(str(err))
                continue
            loc = err.get("loc", [])
            field = loc[-1] if loc else None
            err_type = err.get("type", "")
            friendly = _FIELD_ERROR_MESSAGES.get((field, err_type))
            if friendly:
                messages.append(friendly)
            else:
                messages.append(f"{_friendly_field_name(loc)}: {err.get('msg', 'Invalid value.')}")
        return " ".join(messages) if messages else "Please check your details and try again."

    return "Please check your details and try again."


def _validate_signup_fields(username, email, password, confirm_password):
    """Client-side checks so most bad input never has to round-trip to the
    backend at all — gives instant, precise feedback to the user."""
    if not username or not email or not password or not confirm_password:
        return "Please fill in every field."

    if len(username) < 3:
        return "Username must be at least 3 characters."

    if not EMAIL_RE.match(email):
        return "Please enter a valid email address, like name@example.com."

    if len(password) < 6:
        return "Password must be at least 6 characters."

    if password != confirm_password:
        return "Passwords do not match."

    return None


def create_user(username, email, password, confirm_password):
    username = (username or "").strip()
    email = (email or "").strip()
    password = password or ""
    confirm_password = confirm_password or ""

    field_error = _validate_signup_fields(username, email, password, confirm_password)
    if field_error:
        return False, field_error

    try:
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json={"username": username, "email": email, "password": password},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return False, (
            "Could not connect to the backend. Please make sure your FastAPI "
            "backend is running on http://127.0.0.1:8000."
        )

    if response.status_code == 200:
        return True, "Account created. You can now log in."

    try:
        detail = response.json().get("detail", "Signup failed.")
    except Exception:
        detail = "Signup failed."

    return False, _humanize_validation_errors(detail)


def authenticate_user(identifier, password):
    identifier = (identifier or "").strip()
    password = password or ""

    if not identifier or not password:
        return False, None, "Please enter your username/email and password."

    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"identifier": identifier, "password": password},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return False, None, (
            "Could not connect to the backend. Please make sure your FastAPI "
            "backend is running on http://127.0.0.1:8000."
        )

    if response.status_code == 200:
        data = response.json()
        user = {
            "username": data["user"]["username"],
            "email": data["user"]["email"],
            "token": data["access_token"],
        }
        return True, user, None

    try:
        detail = response.json().get("detail", "Login failed.")
    except Exception:
        detail = "Login failed."

    return False, None, _humanize_validation_errors(detail)

def request_password_reset(email):
    email = (email or "").strip()

    if not email:
        return False, "Please enter your email address."

    if not EMAIL_RE.match(email):
        return False, "Please enter a valid email address, like name@example.com."

    try:
        response = requests.post(
            f"{API_BASE}/auth/forgot-password",
            json={"email": email},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return False, (
            "Could not connect to the backend. Please make sure your FastAPI "
            "backend is running on http://127.0.0.1:8000."
        )

    if response.status_code == 200:
        try:
            message = response.json().get(
                "message",
                "If an account with that email exists, a password reset link has been sent.",
            )
        except Exception:
            message = "If an account with that email exists, a password reset link has been sent."
        return True, message

    try:
        detail = response.json().get("detail", "Something went wrong. Please try again.")
    except Exception:
        detail = "Something went wrong. Please try again."

    return False, _humanize_validation_errors(detail)


def reset_password_with_token(token, new_password, confirm_password):
    token = (token or "").strip()
    new_password = new_password or ""
    confirm_password = confirm_password or ""

    if not token:
        return False, "Invalid reset link."

    if not new_password or not confirm_password:
        return False, "Please fill in both password fields."

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."

    if new_password != confirm_password:
        return False, "Passwords do not match."

    try:
        response = requests.post(
            f"{API_BASE}/auth/reset-password",
            json={"token": token, "new_password": new_password},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return False, (
            "Could not connect to the backend. Please make sure your FastAPI "
            "backend is running on http://127.0.0.1:8000."
        )

    if response.status_code == 200:
        try:
            message = response.json().get("message", "Your password has been reset successfully.")
        except Exception:
            message = "Your password has been reset successfully."
        return True, message

    # The backend intentionally returns the same generic message for
    # invalid, expired, and already-used tokens (400/401/403/404) so we
    # don't try to distinguish those cases here either.
    if response.status_code in (400, 401, 403, 404):
        try:
            detail = response.json().get("detail", "")
        except Exception:
            detail = ""
        return False, detail or (
            "This reset link is invalid or has expired. Please request a new password reset link."
        )

    if response.status_code == 422:
        try:
            detail = response.json().get("detail", "Please check your input and try again.")
        except Exception:
            detail = "Please check your input and try again."
        return False, _humanize_validation_errors(detail)

    return False, "Something went wrong on our end. Please try again in a moment."