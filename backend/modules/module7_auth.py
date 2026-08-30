import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from database.connection import get_db
from database.models import User, PasswordResetToken

import smtplib
from email.message import EmailMessage

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------- Config ----------
# Set AUTH_SECRET_KEY in your .env file for production use.
# Falling back to a default locally so the app still runs without it,
# but tokens signed with the default key should never be trusted in prod.
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "dev-only-change-this-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Set GOOGLE_CLIENT_ID in your .env file to the OAuth Client ID configured
# in Google Cloud Console. Required for /auth/google to work.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# How long a password-reset token stays valid.
RESET_TOKEN_EXPIRE_MINUTES = 30

# ---------- Email (SMTP) Config ----------
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL", "http://localhost:5173/reset-password")

# DEVELOPMENT-ONLY: email sending isn't implemented yet, so when this is
# "true" /auth/forgot-password includes the raw reset token directly in
# its JSON response, purely so the flow can be tested end-to-end via
# Swagger. Set RESET_TOKEN_DEBUG_MODE=false (or unset it) before any
# real/production deployment — search for "DEV-ONLY" below to remove
# this block entirely once real email sending is wired up.
def send_reset_email(to_email: str, raw_token: str) -> None:
    """Sends the password reset link to the user's email via SMTP.
    Raises on failure so the caller can decide how to handle it —
    it never logs or returns the raw token itself."""
    reset_link = f"{FRONTEND_RESET_URL}?token={raw_token}"

    body = (
        "Hello,\n\n"
        "You requested to reset your SalesGenie password.\n\n"
        "Click the link below to reset your password:\n\n"
        f"{reset_link}\n\n"
        "This link will expire in 30 minutes.\n\n"
        "If you did not request this password reset, you can safely ignore this email.\n\n"
        "Regards,\nSalesGenie Team"
    )

    message = EmailMessage()
    message["Subject"] = "Reset your SalesGenie password"
    message["From"] = SMTP_USERNAME
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


# ---------- Pydantic Schemas ----------

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    identifier: str  # username OR email
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class GenericAuthResponse(BaseModel):
    message: str

class MessageResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---------- Password hashing (bcrypt) ----------

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    if not hashed_password:
        # Google-only accounts have no local password to check against.
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def hash_reset_token(raw_token: str) -> str:
    """SHA-256 hash of a raw reset token. Only this hash is ever stored;
    the raw token is shown to the user exactly once and never persisted."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def _unique_username_from_email(email: str, db: Session) -> str:
    """Derive a username from an email's local part, appending a numeric
    suffix if that username is already taken (e.g. by a local account)."""
    base = email.split("@")[0]
    username = base
    suffix = 1
    while db.query(User).filter(User.username == username).first():
        suffix += 1
        username = f"{base}{suffix}"
    return username


# ---------- 1. Signup ----------
@router.post("/signup", response_model=UserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    username = payload.username.strip()
    email = payload.email.strip().lower()

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")

    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    existing = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="An account with that username or email already exists.",
        )

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(payload.password),
        auth_provider="local",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------- 2. Login ----------
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    identifier = payload.identifier.strip().lower()

    user = db.query(User).filter(
        (User.email == identifier) | (User.username.ilike(identifier))
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username/email or password.",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


# ---------- 3. Google Login ----------
@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google login is not configured on this server.",
        )

    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.id_token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google ID token.")

    google_id = idinfo.get("sub")
    email = (idinfo.get("email") or "").strip().lower()

    if not google_id or not email:
        raise HTTPException(status_code=401, detail="Google token missing required claims.")

    if not idinfo.get("email_verified", False):
        raise HTTPException(status_code=401, detail="Google email is not verified.")

    # 1. Existing Google-linked account
    user = db.query(User).filter(User.google_id == google_id).first()

    if not user:
        # 2. An existing local account with the same email - link it
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id
        else:
            # 3. Brand-new account
            user = User(
                username=_unique_username_from_email(email, db),
                email=email,
                hashed_password=None,
                auth_provider="google",
                google_id=google_id,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


# ---------- 4. Current user (for validating a stored token) ----------
@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


# ---------- 5. Forgot Password ----------
# Always returns the exact same generic message, regardless of whether the
# email is registered, unregistered, or belongs to a Google-only account.
_GENERIC_FORGOT_PASSWORD_RESPONSE = {
    "message": "If an account with that email exists, a password reset link has been sent."
}


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    # No account, or a Google-only account with no local password to reset:
    # do nothing, but still return the generic response below so the caller
    # can't distinguish this case from a normal, successful request.
    if not user or user.hashed_password is None:
        return _GENERIC_FORGOT_PASSWORD_RESPONSE

    raw_token = secrets.token_urlsafe(32)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_reset_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        used=False,
    )
    db.add(reset_token)
    db.commit()

    try:
        send_reset_email(user.email, raw_token)
    except Exception:
        # Email sending failed (bad SMTP config, network issue, etc).
        # The token still exists in the database and remains valid until
        # it expires, so this is safe to fail silently to the caller —
        # revealing SMTP errors here would leak infrastructure details
        # and could also confirm account existence.
        pass

    return _GENERIC_FORGOT_PASSWORD_RESPONSE


# ---------- 6. Reset Password ----------
@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    token_hash = hash_reset_token(payload.token)
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()

    invalid_token_exception = HTTPException(
        status_code=400, detail="This reset link is invalid or has expired."
    )

    if not reset_token:
        raise invalid_token_exception

    if reset_token.used:
        raise invalid_token_exception

    expires_at = reset_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise invalid_token_exception

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise invalid_token_exception

    user.hashed_password = hash_password(payload.new_password)
    reset_token.used = True

    db.commit()

    return {"message": "Your password has been reset successfully."}