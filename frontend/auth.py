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