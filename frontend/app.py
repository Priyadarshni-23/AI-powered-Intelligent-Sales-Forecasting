import streamlit as st
from database import init_db
from modules import tabs_view, login_page
from styles import load_css

st.set_page_config(
    page_title="SalesGenie AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
load_css()

# Pick up a completed Google OAuth login (via st.login("google"))
try:
    if getattr(st.user, "is_logged_in", False):
        st.session_state.authenticated = True
        st.session_state.current_user = {
            "username": st.user.get("name") or st.user.get("email") or "Google user",
            "email": st.user.get("email", ""),
        }
except Exception:
    pass

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page.show()
    st.stop()

# ---------------------------------------------------------------
# Authenticated app
# ---------------------------------------------------------------

current_user = st.session_state.get("current_user") or {}
username = current_user.get("username", "Account")
initials = "".join([p[0] for p in username.replace(".", " ").split()[:2]]).upper() or "A"

if "active_section" not in st.session_state:
    st.session_state.active_section = "leads"

logout_clicked = False

with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-avatar">SG</div>
            <div>
                <h1>SalesGenie AI</h1>
                <p>Sales assistant & lead intelligence</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.container(key="nav_group"):
        for key, label in tabs_view.NAV_ITEMS:
            is_active = st.session_state.active_section == key
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_section = key
                st.rerun()

    st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider" />', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="sidebar-user-chip">
            <div class="sidebar-user-avatar">{initials}</div>
            <div>
                <div class="sidebar-user-name">{username}</div>
                <div class="sidebar-user-role">Account</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    logout_clicked = st.button("Log out", key="logout_btn", use_container_width=True)

if logout_clicked:
    st.session_state.authenticated = False
    st.session_state.current_user = None
    try:
        if getattr(st.user, "is_logged_in", False):
            st.logout()
    except Exception:
        pass
    st.rerun()

tabs_view.render(st.session_state.active_section)