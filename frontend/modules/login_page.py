import base64
import time
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from auth import create_user, authenticate_user, request_password_reset, reset_password_with_token

APP_DIR = Path(__file__).resolve().parent


# ── Splash screen ────────────────────────────────────────────────────────
SPLASH_DURATION_SECONDS = 2.7  # must match the total animation sequence below


def _bg_image_base64(path=None):
    if path is None:
        path = APP_DIR / "assets" / "splash_bg.png"
    try:
        data = Path(path).read_bytes()
        return base64.b64encode(data).decode()
    except Exception:
        return None


def _render_splash():
    # The full-page background image is already painted behind everything by
    # _inject_login_page_background() (called in _show_splash_then_continue
    # before this iframe renders). Painting the image a second time here, on
    # just the iframe's own box, produced a visible seam/duplicate corner
    # where the iframe's crop of the image didn't line up with the page's
    # crop. So this inner layer stays transparent and lets the page
    # background show through underneath.
    html = f"""
<html>
<head>
<style>
    html, body {{
        margin: 0;
        padding: 0;
        background: transparent;
    }}
    .splash-outer {{
        background: transparent;
        min-height: 680px;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Source Sans Pro', 'Segoe UI', sans-serif;
    }}
    .splash-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        animation: splash-fade-in 0.5s ease-out;
    }}
    @keyframes splash-fade-in {{
        0%   {{ opacity: 0; transform: translateY(12px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .splash-title {{
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #d94f1e, #f0961a 45%, #e0692a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 12px;
    }}
    .splash-subtitle {{
        font-size: 1.05rem;
        font-weight: 500;
        color: #7a5a3a;
        margin-bottom: 36px;
        letter-spacing: 0.2px;
    }}

    .growth-stage {{
        position: relative;
        width: 340px;
        height: 220px;
    }}

    .glow-orb {{
        position: absolute;
        top: -10px;
        right: 18px;
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,196,80,0.6), rgba(255,196,80,0) 70%);
        opacity: 0;
        animation: glow-in 0.6s ease-out 2.0s forwards;
    }}
    @keyframes glow-in {{
        0%   {{ opacity: 0; transform: scale(0.7); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}

    .bars {{
        position: absolute;
        bottom: 0;
        left: 0;
        display: flex;
        align-items: flex-end;
        gap: 16px;
        width: 100%;
        height: 170px;
    }}
    .bar {{
        width: 34px;
        border-radius: 8px 8px 0 0;
        background: linear-gradient(180deg, #ffce6b, #e0862a);
        transform: scaleY(0);
        transform-origin: bottom;
        animation: bar-grow 0.5s cubic-bezier(0.22, 0.9, 0.3, 1) forwards;
    }}
    .bar1 {{ height: 60px;  animation-delay: 0.0s;  }}
    .bar2 {{ height: 95px;  animation-delay: 0.4s;  }}
    .bar3 {{ height: 75px;  animation-delay: 0.8s;  }}
    .bar4 {{ height: 135px; animation-delay: 1.2s;  }}
    .bar5 {{ height: 170px; animation-delay: 1.6s;  }}
    @keyframes bar-grow {{
        0%   {{ transform: scaleY(0); }}
        100% {{ transform: scaleY(1); }}
    }}

    .trend-line {{
        position: absolute;
        bottom: 0;
        left: 0;
        width: 340px;
        height: 220px;
        overflow: visible;
    }}
    .trend-path {{
        fill: none;
        stroke: #b0491c;
        stroke-width: 3;
        stroke-linecap: round;
        stroke-dasharray: 320;
        stroke-dashoffset: 320;
        opacity: 0;
        animation: draw-line 0.9s ease-out 1.6s forwards;
    }}
    @keyframes draw-line {{
        0%   {{ stroke-dashoffset: 320; opacity: 0; }}
        5%   {{ opacity: 1; }}
        100% {{ stroke-dashoffset: 0; opacity: 1; }}
    }}

    .sparkle {{
        position: absolute;
        width: 16px;
        height: 16px;
        opacity: 0;
        transform: scale(0.3);
        animation: sparkle-in 0.5s ease-out forwards;
    }}
    .sparkle svg {{ width: 100%; height: 100%; }}
    .spk1 {{ top: -18px; right: 40px; animation-delay: 2.1s; }}
    .spk2 {{ top: 6px;   right: 90px; animation-delay: 2.25s; }}
    .spk3 {{ top: -34px; right: 90px; animation-delay: 2.35s; }}
    @keyframes sparkle-in {{
        0%   {{ opacity: 0; transform: scale(0.3) rotate(0deg); }}
        60%  {{ opacity: 1; transform: scale(1.15) rotate(70deg); }}
        100% {{ opacity: 1; transform: scale(1) rotate(90deg); }}
    }}
</style>
</head>
<body>
    <div class="splash-outer">
        <div class="splash-wrap">
            <div class="splash-title">Welcome to AI Sales Forecast</div>
            <div class="splash-subtitle">Turning your leads into revenue</div>

            <div class="growth-stage">
                <div class="glow-orb"></div>

                <div class="sparkle spk1"><svg viewBox="0 0 24 24"><path d="M12 0 L14 10 L24 12 L14 14 L12 24 L10 14 L0 12 L10 10 Z" fill="#ffd45c"/></svg></div>
                <div class="sparkle spk2"><svg viewBox="0 0 24 24"><path d="M12 0 L14 10 L24 12 L14 14 L12 24 L10 14 L0 12 L10 10 Z" fill="#ff9a3c"/></svg></div>
                <div class="sparkle spk3"><svg viewBox="0 0 24 24"><path d="M12 0 L14 10 L24 12 L14 14 L12 24 L10 14 L0 12 L10 10 Z" fill="#ffd45c"/></svg></div>

                <svg class="trend-line" viewBox="0 0 340 220" xmlns="http://www.w3.org/2000/svg">
                    <path class="trend-path" d="M17,150 L67,90 L117,110 L167,45 L217,15"/>
                </svg>

                <div class="bars">
                    <div class="bar bar1"></div>
                    <div class="bar bar2"></div>
                    <div class="bar bar3"></div>
                    <div class="bar bar4"></div>
                    <div class="bar bar5"></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    components.html(html, height=700, scrolling=False)


def _show_splash_then_continue():
    """Render the splash once, hold for the full animation sequence, then jump straight to login."""
    _inject_login_page_background()
    placeholder = st.empty()
    with placeholder.container():
        _render_splash()
    time.sleep(SPLASH_DURATION_SECONDS)
    placeholder.empty()
    st.session_state.splash_shown = True
    st.rerun()


def _inject_login_page_background():
    """Apply the same background image used on the splash screen to the actual page canvas."""
    bg_b64 = _bg_image_base64()
    if bg_b64:
        bg_css = (
            f"background-image: url(data:image/png;base64,{bg_b64});"
            "background-size: cover; background-position: center; background-attachment: fixed;"
        )
    else:
        bg_css = "background: linear-gradient(135deg, #f3d9b8, #fbeee0, #f0c896);"

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            {bg_css}
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Existing login/signup code ───────────────────────────────────────────

def _google_configured():
    """
    True only if Google OAuth credentials have been added to
    .streamlit/secrets.toml under [auth.google]. Without this,
    Streamlit's native st.login("google") has nothing to connect to.
    """
    try:
        return bool(st.secrets.get("auth", {}).get("google", {}).get("client_id"))
    except Exception:
        return False


def _try_google_login():
    if not _google_configured():
        st.warning(
            "Google sign-in isn't configured yet. Add your Google OAuth client "
            "credentials to `.streamlit/secrets.toml` under `[auth.google]` "
            "(client_id, client_secret) and a top-level `[auth]` block "
            "(redirect_uri, cookie_secret) to enable this button. See "
            "docs.streamlit.io for `st.login`."
        )
        return

    try:
        st.login("google")
    except Exception as e:
        st.error(f"Google sign-in failed to start: {e}")


def _brand_panel():
    st.markdown(
        """
        <div class="login-brand-panel">
            <div class="login-brand-avatar">AF</div>
            <h1>AI Sales Forecast</h1>
            <p class="login-brand-tag">
                Your AI-powered sales assistant &mdash; qualify leads, write
                outreach, and track your pipeline in one place.
            </p>
            <ul class="login-brand-features">
                <li><span class="dot"></span>Smart lead scoring &amp; qualification</li>
                <li><span class="dot"></span>AI-generated outreach in seconds</li>
                <li><span class="dot"></span>Real-time pipeline &amp; performance insights</li>
                <li><span class="dot"></span>One-click CRM sync</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _header(title, subtitle):
    st.markdown(
        f"""
        <div class="login-form-title">{title}</div>
        <div class="login-form-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def _render_login_form():
    _header("Welcome back", "Sign in to access your leads")

    with st.form("login_form"):
        identifier = st.text_input(
            "Username or Email", placeholder="you@example.com"
        )
        password = st.text_input(
            "Password", type="password", placeholder="••••••••"
        )
        submitted = st.form_submit_button("Log In", use_container_width=True)

    if submitted:
        ok, user, error = authenticate_user(identifier, password)

        if ok:
            st.session_state.authenticated = True
            st.session_state.current_user = user
            st.rerun()
        else:
            st.error(error)

    if st.button("Forgot Password?", key="go_forgot_password_btn", use_container_width=True):
        st.session_state.auth_mode = "forgot_password"
        st.rerun()

    st.markdown('<div class="login-divider"><span>or</span></div>', unsafe_allow_html=True)

    if st.button("Continue with Google", use_container_width=True, key="google_login_btn"):
        _try_google_login()

    st.markdown(
        '<p class="login-footer">New to AI Sales Forecast?</p>',
        unsafe_allow_html=True,
    )

    if st.button("Create Account", use_container_width=True, key="go_signup_btn"):
        st.session_state.auth_mode = "signup"
        st.rerun()


def _render_signup_form():
    _header("Create your account", "Start managing leads with AI Sales Forecast")

    with st.form("signup_form"):
        username = st.text_input("Username", placeholder="janedoe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input(
            "Password", type="password", placeholder="At least 6 characters"
        )
        confirm_password = st.text_input(
            "Confirm Password", type="password", placeholder="Re-enter password"
        )
        submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            ok, message = create_user(username, email, password, confirm_password)
            if ok:
                st.success(message)
                st.session_state.auth_mode = "login"
            else:
                st.error(message)

    st.markdown('<div class="login-divider"><span>or</span></div>', unsafe_allow_html=True)

    if st.button("Continue with Google", use_container_width=True, key="google_signup_btn"):
        _try_google_login()

    if st.button("Back to Log In", use_container_width=True, key="go_login_btn"):
        st.session_state.auth_mode = "login"
        st.rerun()

def _render_forgot_password_form():
    _header(
        "Forgot Password?",
        "Enter your registered email address and we'll send you a link to reset your password.",
    )

    with st.form("forgot_password_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        submitted = st.form_submit_button("Send Reset Link", use_container_width=True)

        if submitted:
            with st.spinner("Sending reset link..."):
                ok, message = request_password_reset(email)
            if ok:
                st.session_state.forgot_password_sent = True
                st.session_state.forgot_password_message = message
            else:
                st.session_state.forgot_password_sent = False
                st.error(message)

    if st.session_state.get("forgot_password_sent"):
        st.success("Reset link sent successfully.")
        st.info("Please check your email for the password reset link.")

    if st.button("Back to Login", key="forgot_back_to_login_btn", use_container_width=True):
        st.session_state.auth_mode = "login"
        st.session_state.forgot_password_sent = False
        st.rerun()


def _render_reset_password_form():
    _header("Reset Password", "Choose a new password for your account")

    token = st.session_state.get("reset_token")

    if not token:
        st.error("Invalid reset link.")
        if st.button("Request New Reset Link", key="invalid_token_request_new_btn", use_container_width=True):
            st.session_state.auth_mode = "forgot_password"
            st.rerun()
        return

    if st.session_state.get("reset_password_success"):
        st.success("Password Reset Successfully")
        st.write("Your password has been updated successfully.")
        if st.button("Go to Login", key="reset_success_go_login_btn", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.session_state.reset_password_success = False
            st.session_state.reset_token = None
            st.query_params.clear()
            st.rerun()
        return

    with st.form("reset_password_form"):
        new_password = st.text_input(
            "New Password", type="password", placeholder="At least 6 characters"
        )
        confirm_password = st.text_input(
            "Confirm Password", type="password", placeholder="Re-enter new password"
        )
        submitted = st.form_submit_button("Reset Password", use_container_width=True)

        if submitted:
            with st.spinner("Resetting your password..."):
                ok, message = reset_password_with_token(token, new_password, confirm_password)
            if ok:
                st.session_state.reset_password_success = True
                st.rerun()
            else:
                is_token_error = "invalid or has expired" in message.lower() or "invalid reset link" in message.lower()
                st.error(message)
                if is_token_error:
                    if st.button(
                        "Request New Reset Link", key="reset_failed_request_new_btn", use_container_width=True
                    ):
                        st.session_state.auth_mode = "forgot_password"
                        st.session_state.reset_token = None
                        st.query_params.clear()
                        st.rerun()

    if st.button("Back to Login", key="reset_back_to_login_btn", use_container_width=True):
        st.session_state.auth_mode = "login"
        st.session_state.reset_token = None
        st.query_params.clear()
        st.rerun()


def show():
    # If the URL contains a reset token (the user clicked the emailed
    # reset link), go straight to the reset-password form — skip the
    # splash screen and whatever auth_mode was previously set.
    url_token = st.query_params.get("token")
    if url_token and not st.session_state.get("reset_password_success"):
        st.session_state.reset_token = url_token
        st.session_state.auth_mode = "reset_password"
        st.session_state.splash_shown = True

    # ── Splash gate: show once per session before anything else ──────────
    if not st.session_state.get("splash_shown", False):
        _show_splash_then_continue()
        return  # stop here; rerun triggered above will land back in show()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    _inject_login_page_background()

    st.markdown('<div class="login-page">', unsafe_allow_html=True)

    with st.container(key="login_shell"):
        col_brand, col_form = st.columns([1, 1.1], vertical_alignment="center")

        with col_brand:
            _brand_panel()

        with col_form:
            with st.container(key="login_form_panel"):
                if st.session_state.auth_mode == "login":
                    _render_login_form()
                elif st.session_state.auth_mode == "signup":
                    _render_signup_form()
                elif st.session_state.auth_mode == "forgot_password":
                    _render_forgot_password_form()
                elif st.session_state.auth_mode == "reset_password":
                    _render_reset_password_form()

    st.markdown("</div>", unsafe_allow_html=True)