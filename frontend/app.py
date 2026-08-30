import streamlit as st
from database import init_db
from modules import tabs_view, login_page
from styles import load_css

st.set_page_config(
    page_title="AI Sales Forecast",
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

if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False

logout_clicked = False
collapsed = st.session_state.sidebar_collapsed

with st.sidebar:
    # Width + spacing driven by our own collapsed flag rather than
    # Streamlit's native collapse (which hides the sidebar completely).
    # This lets it shrink to a narrow icon rail instead of disappearing.
    rail_width = "68px" if collapsed else "264px"
    side_pad = "6px" if collapsed else "16px"
    collapsed_nav_css = ""
    if collapsed:
        collapsed_nav_css = (
            'html body section[data-testid="stSidebar"] .stButton > button {'
            "justify-content: center !important;"
            "padding: 12px 0 !important;"
            "}"
            'html body section[data-testid="stSidebar"] .stButton [data-testid="stIconMaterial"] {'
            "font-size: 24px !important;"
            "}"
            'html body section[data-testid="stSidebar"] .st-key-sidebar_toggle button {'
            "width: 32px !important;"
            "min-width: 32px !important;"
            "margin: 0 auto !important;"
            "background: var(--brown-50) !important;"
            "}"
            # Extra top margin on the toggle's own wrapper element so it
            # never sits flush under the logo above it, regardless of the
            # logo's inline margin.
            'html body section[data-testid="stSidebar"] .st-key-sidebar_toggle {'
            "margin-top: 10px !important;"
            "}"
            'html body section[data-testid="stSidebar"] .st-key-sidebar_toggle [data-testid="stIconMaterial"] {'
            "font-size: 17px !important;"
            "}"
        )
    mobile_rail_width = "64px" if collapsed else "min(78vw, 280px)"
    st.markdown(
        f"""
        <style>
        html body section[data-testid="stSidebar"] {{
            min-width: {rail_width} !important;
            max-width: {rail_width} !important;
        }}
        html body section[data-testid="stSidebar"] > div {{
            padding: 10px {side_pad} 16px {side_pad} !important;
        }}
        {collapsed_nav_css}

        /* On phones/small tablets the sidebar becomes a slide-over drawer,
           so give it a touch-friendly width instead of the fixed desktop
           rail/panel widths above. */
        @media (max-width: 768px) {{
            html body section[data-testid="stSidebar"] {{
                min-width: {mobile_rail_width} !important;
                max-width: {mobile_rail_width} !important;
            }}
            html body section[data-testid="stSidebar"] .stButton > button {{
                min-height: 44px !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if collapsed:
        st.markdown(
            '<div class="sidebar-logo-static" style="margin-bottom:22px;">AF</div>',
            unsafe_allow_html=True,
        )
        toggle_clicked = st.button(
            "",
            icon=":material/left_panel_open:",
            key="sidebar_toggle",
            help="Expand sidebar",
            use_container_width=True,
        )
    else:
        with st.container(key="sidebar_header"):
            col_logo, col_text, col_toggle = st.columns(
                [1, 3.0, 0.7], gap="small", vertical_alignment="center"
            )
            with col_logo:
                st.markdown('<div class="sidebar-logo-static">AF</div>', unsafe_allow_html=True)
            with col_text:
                st.markdown("""
                    <div class="sidebar-brand-text">
                        <h1>AI Sales Forecast</h1>
                        <p>Intelligent Sales Prediction &amp; Analytics</p>
                    </div>
                """, unsafe_allow_html=True)
            with col_toggle:
                toggle_clicked = st.button(
                    "",
                    icon=":material/left_panel_close:",
                    key="sidebar_toggle",
                    help="Collapse sidebar",
                )

    if toggle_clicked:
        st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
        st.rerun()

    if collapsed:
        # A visible divider (rather than a bare spacer) so the toggle
        # button is clearly its own element sitting between the logo and
        # the "Leads" tab, instead of blending into the nav icon list.
        st.markdown('<hr class="sidebar-divider-collapsed" />', unsafe_allow_html=True)
    # (Expanded-mode spacing between the header and "Leads" is handled by
    # the .st-key-sidebar_header margin-bottom in styles.py.)

    with st.container(key="nav_group"):
        for key, label, icon in tabs_view.NAV_ITEMS:
            is_active = st.session_state.active_section == key
            if st.button(
                "" if collapsed else label,
                icon=f":material/{icon}:",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                help=label if collapsed else None,
            ):
                st.session_state.active_section = key
                st.rerun()

    st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider" />', unsafe_allow_html=True)

    if collapsed:
        st.markdown(
            f'<div class="sidebar-user-avatar-collapsed" title="{username}">{initials}</div>',
            unsafe_allow_html=True,
        )
        logout_clicked = st.button(
            "",
            icon=":material/logout:",
            key="logout_btn",
            use_container_width=True,
            help="Log out",
        )
    else:
        st.markdown(f"""
            <div class="sidebar-user-chip">
                <div class="sidebar-user-avatar">{initials}</div>
                <div>
                    <div class="sidebar-user-name">{username}</div>
                    <div class="sidebar-user-role">Account</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        logout_clicked = st.button(
            "Log out",
            icon=":material/logout:",
            key="logout_btn",
            use_container_width=True,
        )

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