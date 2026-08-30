import base64
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).resolve().parent


def _app_bg_image_base64():
    path = APP_DIR / "modules" / "assets" / "app_bg.png"
    try:
        return base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return None


def load_css():
    bg_b64 = _app_bg_image_base64()
    if bg_b64:
        app_bg_css = (
            f"background-image: url(data:image/png;base64,{bg_b64});"
            "background-size: cover; background-position: center; "
            "background-attachment: fixed; background-repeat: no-repeat;"
        )
    else:
        app_bg_css = "background: radial-gradient(circle at 0% 0%, #fbf4ec 0%, #f6efe6 45%, #f3ece2 100%);"

    # Applied on every page. The login page (modules/login_page.py) paints its
    # own background image on top of [data-testid="stAppViewContainer"], so it
    # is unaffected by this and keeps its separate splash_bg.png.
    st.markdown(
        f"""
        <style>
        .stApp {{
            {app_bg_css}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 16px;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
    /* Prevent the main content column from being stretched to match the
       sidebar's full-viewport height — that was leaving blank space below
       shorter pages like Leads. Main content should only be as tall as
       its own content. */
    div[data-testid="stAppViewContainer"] {
        align-items: flex-start !important;
    }

    /* =========================================================
       TAILWIND-STYLE UTILITY LAYER
       (hand-rolled locally since Tailwind's CDN <script> cannot
       execute inside Streamlit's React-rendered markdown/DOM —
       these utilities give the same authoring model & result)
       ========================================================= */
    :root {
        --brown-50:  #fdf8f2;
        --brown-100: #fbf1e4;
        --brown-200: #f1e6da;
        --brown-300: #e8ddd0;
        --brown-400: #d8ac7a;
        --brown-500: #b5651d;
        --brown-600: #8a4b1f;
        --brown-700: #6b3a18;
        --brown-800: #4a2e1a;
        --brown-900: #3d2817;
        --white: #ffffff;

        /* Sidebar / login premium accent palette (calm, muted — not near-black, not warm/orange) */
        --ink-900: #3a2f28;
        --ink-800: #453830;
        --ink-700: #57453a;
        --gold-300: #f0c674;
        --gold-400: #e8b455;
        --gold-500: #e0a83e;
        --gold-600: #c98a26;
        --gold-700: #a36f1e;
        --cream-text: #fbf6ee;
    }
    .flex { display: flex; }
    .items-center { align-items: center; }
    .justify-between { justify-content: space-between; }
    .gap-2 { gap: 8px; }
    .gap-3 { gap: 12px; }
    .gap-4 { gap: 16px; }
    .rounded-xl { border-radius: 12px; }
    .rounded-2xl { border-radius: 18px; }
    .rounded-full { border-radius: 999px; }
    .shadow-sm { box-shadow: 0 1px 2px rgba(74, 46, 26, 0.06); }
    .shadow-md { box-shadow: 0 4px 14px rgba(74, 46, 26, 0.08); }
    .shadow-lg { box-shadow: 0 10px 30px rgba(74, 46, 26, 0.10); }
    .border-brown { border: 1px solid var(--brown-300); }
    .bg-white { background: var(--white); }
    .bg-brown-50 { background: var(--brown-50); }
    .bg-gradient-brown {
        background: linear-gradient(135deg, var(--brown-500) 0%, var(--brown-700) 100%);
    }
    .text-brown-900 { color: var(--brown-900); }
    .text-brown-600 { color: var(--brown-600); }
    .text-muted { color: #a3927e; }
    .font-poppins { font-family: 'Poppins', 'Inter', sans-serif; }
    .tracking-tight { letter-spacing: -0.02em; }
    .transition { transition: all 0.18s ease; }

    /* ---------- Sidebar (side-panel navigation) ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fdf8f2 0%, #f8f1e6 55%, #fdf8f2 100%) !important;
        border-right: 1px solid var(--brown-200) !important;
        min-width: 264px !important;
        max-width: 264px !important;
        transition: min-width 0.22s ease, max-width 0.22s ease !important;
        overflow-x: hidden !important;
    }
    section[data-testid="stSidebar"] > div {
        padding: 10px 16px 16px 16px !important;
        height: 100vh;
        display: flex;
        flex-direction: column;
        transition: padding 0.22s ease;
    }
    /* Hide the sidebar's scrollbar entirely — it should never show a visible
       scroll track. The sidebar still scrolls if content is ever taller than
       the viewport on a very short window, but no track/thumb is painted, so
       it always reads as a clean, spacious panel like the reference design. */
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        overflow-y: auto !important;
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    section[data-testid="stSidebar"] > div::-webkit-scrollbar,
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar,
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"]::-webkit-scrollbar {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }
    /* We drive collapse/expand entirely from our own toggle (the logo),
       so the native Streamlit collapse arrow is hidden — it would fight
       with our own state and fully hide the sidebar instead of shrinking
       it to an icon rail. */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        height: 100%;
        display: flex;
        flex-direction: column;
        gap: 6px !important;
    }
    /* pushes everything after it (divider, user chip, logout) to the bottom
       of the sidebar so logout never requires scrolling to reach */
    .sidebar-spacer {
        margin-top: auto;
    }
    /* nav button group spreads evenly across the free vertical space
       in the sidebar instead of bunching at the top */
    .st-key-nav_group {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
        min-height: 0;
    }
    .st-key-nav_group [data-testid="stVerticalBlock"] {
        gap: 4px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--brown-800);
    }
    .block-container {
        padding-top: 1.75rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 1.5rem;
        max-width: 100%;
    }

    /* ---------- Sidebar brand ---------- */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 26px;
        padding: 0 6px;
    }
    .sidebar-brand-avatar {
        width: 42px;
        height: 42px;
        min-width: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--gold-500) 0%, var(--gold-700) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--ink-900);
        font-weight: 800;
        font-size: 16px;
        font-family: 'Poppins', 'Inter', sans-serif;
        box-shadow: 0 6px 16px rgba(224, 168, 62, 0.35);
    }
    .sidebar-brand h1 {
        color: var(--brown-900) !important;
        font-size: 18.5px;
        margin: 0;
        font-family: 'Poppins', 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.01em;
        line-height: 1.25;
    }
    .sidebar-brand p {
        color: var(--brown-500);
        font-size: 10.5px;
        margin: 1px 0 0 0;
        font-weight: 500;
    }

    /* ---------- Sidebar logo (static avatar, no longer a toggle) ---------- */
    .sidebar-logo-static {
        width: 42px;
        height: 42px;
        min-width: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--gold-500) 0%, var(--gold-700) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--ink-900);
        font-weight: 800;
        font-size: 15px;
        font-family: 'Poppins', 'Inter', sans-serif;
        box-shadow: 0 6px 16px rgba(224, 168, 62, 0.35);
        margin: 0 auto;
    }
    /* ---------- Sidebar collapse/expand toggle button ----------
       A dedicated ghost icon button (Material "panel" glyphs), separate
       from the logo, matching the small toggle shown in the reference. */
    .st-key-sidebar_toggle button {
        background: transparent !important;
        border: 1px solid var(--brown-200) !important;
        border-radius: 8px !important;
        color: var(--brown-600) !important;
        width: 32px !important;
        min-width: 32px !important;
        height: 32px !important;
        min-height: 32px !important;
        padding: 0 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    .st-key-sidebar_toggle button:hover {
        background: var(--brown-100) !important;
        border-color: var(--brown-300) !important;
        color: var(--brown-900) !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .st-key-sidebar_toggle [data-testid="stIconMaterial"] {
        font-size: 17px !important;
    }
    .sidebar-brand-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 0;
    }
    .sidebar-brand-text h1 {
        color: var(--brown-900) !important;
        font-size: 16.5px;
        margin: 0;
        font-family: 'Poppins', 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.01em;
        line-height: 1.3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sidebar-brand-text p {
        color: var(--brown-500);
        font-size: 10.5px;
        margin: 3px 0 0 0;
        font-weight: 500;
        line-height: 1.35;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* Header block (logo + title + collapse toggle) in expanded mode —
       margin-bottom keeps clear breathing room before the "Leads" tab so
       the two never look like one connected block. */
    .st-key-sidebar_header {
        margin-bottom: 26px !important;
    }
    /* Collapsed-only avatar substitute for the user chip */
    .sidebar-user-avatar-collapsed {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        margin: 4px auto 12px auto;
        background: linear-gradient(135deg, var(--gold-500) 0%, var(--gold-700) 100%);
        color: var(--ink-900);
        font-weight: 800;
        font-size: 12px;
        font-family: 'Poppins', 'Inter', sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .sidebar-live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(224, 168, 62, 0.14);
        border: 1px solid rgba(224, 168, 62, 0.4);
        color: var(--gold-700);
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 5px 12px;
        border-radius: 999px;
        margin: 16px 6px 18px 6px;
    }
    .sidebar-live-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #2f9e5c;
        box-shadow: 0 0 6px rgba(47, 158, 92, 0.5);
    }
    .sidebar-nav-label {
        color: #b7a493;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 4px 10px 8px 10px;
    }

    /* ---------- Sidebar nav buttons ---------- */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: var(--brown-700) !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        margin-bottom: 3px !important;
        box-shadow: none !important;
        transform: none !important;
        gap: 10px !important;
    }
    section[data-testid="stSidebar"] .stButton [data-testid="stIconMaterial"] {
        font-size: 19px !important;
        color: inherit !important;
    }
    section[data-testid="stSidebar"] .stButton > button p {
        text-align: left !important;
        font-weight: inherit !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--brown-100) !important;
        color: var(--brown-900) !important;
        border-color: transparent !important;
        transform: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"],
    section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, var(--gold-500) 0%, var(--gold-600) 100%) !important;
        color: var(--ink-900) !important;
        border-color: transparent !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(224, 168, 62, 0.3) !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] p,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p {
        color: var(--ink-900) !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"]:hover,
    section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, var(--gold-400) 0%, var(--gold-500) 100%) !important;
        transform: translateX(2px) !important;
    }

    .sidebar-divider {
        border: none;
        border-top: 1px solid var(--brown-200);
        margin: 16px 4px;
    }
    /* Separates the collapse/expand toggle from the nav icons below it
       when the sidebar is collapsed, so the toggle reads as its own
       control between the logo and the first tab rather than blending
       into the nav icon list. */
    .sidebar-divider-collapsed {
        border: none;
        border-top: 1px solid var(--brown-200);
        margin: 12px 10px 14px 10px;
    }

    /* ---------- Sidebar user chip + logout ---------- */
    .sidebar-user-chip {
        display: flex;
        align-items: center;
        gap: 10px;
        background: var(--brown-50);
        border: 1px solid var(--brown-200);
        border-radius: 12px;
        padding: 12px 14px;
        margin: 4px 2px 16px 2px;
    }
    .sidebar-user-avatar {
        width: 32px;
        height: 32px;
        min-width: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--gold-500) 0%, var(--gold-700) 100%);
        color: var(--ink-900);
        font-weight: 800;
        font-size: 12px;
        font-family: 'Poppins', 'Inter', sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .sidebar-user-name {
        color: var(--brown-900);
        font-size: 13.5px;
        font-weight: 650;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .sidebar-user-role {
        color: var(--brown-500);
        font-size: 10.5px;
        margin-top: 1px;
    }
    section[data-testid="stSidebar"] .st-key-logout_btn button {
        background: rgba(192, 57, 43, 0.07) !important;
        border: 1px solid rgba(192, 57, 43, 0.3) !important;
        color: #c0392b !important;
        text-align: center !important;
        justify-content: center !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] .st-key-logout_btn button p {
        text-align: center !important;
    }
    section[data-testid="stSidebar"] .st-key-logout_btn button:hover {
        background: #c0392b !important;
        color: #ffffff !important;
        border-color: #c0392b !important;
    }

    /* ---------- Tab bar ---------- */
    .stTabs [role="tablist"] {
        display: flex !important;
        width: 100% !important;
        justify-content: space-between !important;
        gap: 6px !important;
        background: #ffffff !important;
        border: 1px solid var(--brown-200) !important;
        border-radius: 999px !important;
        padding: 6px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 4px 14px rgba(74, 46, 26, 0.06) !important;
    }
    .stTabs [data-testid="stTab"] {
        flex: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 44px !important;
        padding: 0 16px !important;
        background: transparent !important;
        border-radius: 999px !important;
        color: var(--brown-700) !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }
    .stTabs [data-testid="stTab"] p {
        color: inherit !important;
        font-weight: inherit !important;
        margin: 0 !important;
    }
    .stTabs [data-testid="stTab"]:hover {
        background: var(--brown-50) !important;
        color: var(--brown-600) !important;
    }
    .stTabs [data-testid="stTab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--brown-500) 0%, var(--brown-600) 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(181, 101, 29, 0.38), inset 0 1px 0 rgba(255,255,255,0.15) !important;
        transform: translateY(-1px);
    }
    .stTabs [data-testid="stTab"][aria-selected="true"] p {
        color: #ffffff !important;
    }
    .stTabs .react-aria-SelectionIndicator {
        display: none !important;
    }

    /* ---------- Section title ---------- */
    .section-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: var(--brown-800);
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .section-subtitle {
        color: #a3927e;
        font-size: 14.5px;
        margin: 0 0 18px 0;
    }
    .dashboard-caption {
        color: var(--brown-600);
        opacity: 0.75;
        font-size: 13.5px;
        margin-top: 14px;
    }

    /* ---------- Stat cards ---------- */
    /* Equal-height stat cards per row, same technique as the Best
       Actions cards: :has() catches every ancestor wrapper of
       .stat-card regardless of Streamlit's exact internal DOM, so a
       longer label (e.g. "PROPOSAL SENT LEADS" wrapping to two lines)
       can't leave that one card taller/shorter than its row-mates. */
    div[data-testid="stHorizontalBlock"]:has(.stat-card) {
        align-items: stretch !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.stat-card) div[data-testid="stColumn"]:has(.stat-card) {
        display: flex !important;
        flex-direction: column !important;
        height: auto !important;
        min-height: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.stat-card) div[data-testid="stColumn"]:has(.stat-card) div:has(.stat-card) {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        min-height: 0 !important;
        width: 100%;
    }
    .stat-card {
        position: relative;
        background: #ffffff;
        border-radius: 16px;
        padding: 20px 20px 18px 20px;
        border: 1px solid var(--brown-200);
        box-shadow: 0 1px 2px rgba(74, 46, 26, 0.05);
        transition: all 0.2s ease;
        overflow: hidden;
        box-sizing: border-box;
        width: 100%;
        flex: 1 1 auto;
        min-height: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .stat-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px rgba(74, 46, 26, 0.10);
        border-color: var(--brown-300);
    }
    .stat-icon {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        margin-bottom: 12px;
        background: var(--brown-50);
    }
    .stat-label {
        font-size: 12.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        color: #a3927e;
        white-space: normal;
        overflow-wrap: break-word;
        min-height: 2.6em;
        display: flex;
        align-items: flex-end;
        flex: 0 0 auto;
    }
    .stat-value {
        font-family: 'Poppins', 'Inter', sans-serif;
        color: var(--brown-900);
        font-size: 32px;
        font-weight: 700;
        line-height: 1.1;
        flex: 0 0 auto;
    }
    .stat-card.c1::before { background: var(--brown-500); }
    .stat-card.c2::before { background: #c0392b; }
    .stat-card.c3::before { background: #b7791f; }
    .stat-card.c4::before { background: #2f6f4f; }
    .stat-card.c5::before { background: #5c6f8a; }
    .stat-card.c1 .stat-value { color: var(--brown-500); }
    .stat-card.c2 .stat-value { color: #c0392b; }
    .stat-card.c3 .stat-value { color: #b7791f; }
    .stat-card.c4 .stat-value { color: #2f6f4f; }
    .stat-card.c5 .stat-value { color: #5c6f8a; }
    .stat-card.c1 .stat-icon { background: #fdeee0; }
    .stat-card.c2 .stat-icon { background: #fbe1dc; }
    .stat-card.c3 .stat-icon { background: #faf0d7; }
    .stat-card.c4 .stat-icon { background: #e3ede8; }
    .stat-card.c5 .stat-icon { background: #e7ebf1; }

    /* ---------- Lead cards ---------- */
    .lead-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 8px;
        border: 1px solid var(--brown-200);
        border-left: 3px solid var(--brown-500);
        transition: all 0.15s ease;
    }
    .lead-company {
        font-size: 17px;
        font-weight: 700;
        color: var(--brown-900);
    }
    .lead-meta {
        font-size: 14px;
        color: #8a7563;
        margin-top: 3px;
    }

    /* ---------- Bordered containers as elevated cards ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border-color: var(--brown-200) !important;
        background: #ffffff;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.lead-list-item) {
        margin-bottom: 8px;
        transition: all 0.15s ease;
        box-shadow: 0 1px 2px rgba(74, 46, 26, 0.04);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.lead-list-item):hover {
        border-color: var(--brown-400) !important;
        box-shadow: 0 4px 12px rgba(74, 46, 26, 0.08);
    }

    /* ---------- Form subsection headers (#### inside forms/panels) ---------- */
    .stForm h4, .stApp h4 {
        color: var(--brown-700) !important;
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 15.5px !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 1px solid var(--brown-200);
        padding-bottom: 8px;
        margin: 18px 0 14px 0 !important;
    }
    .stForm h4:first-of-type {
        margin-top: 4px !important;
    }

    /* ---------- Scrollbars ---------- */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #f1e6da;
        border-radius: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background: #d8ac7a;
        border-radius: 8px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #b5651d;
    }

    /* ---------- Leads master-detail layout ---------- */
    .lead-list-item {
        padding-bottom: 10px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.lead-list-item-active) {
        border-color: var(--brown-500) !important;
        background: var(--brown-50) !important;
        box-shadow: 0 4px 12px rgba(181, 101, 29, 0.12) !important;
    }
    .lead-empty-state {
        background: #ffffff;
        border: 1px dashed var(--brown-300);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        color: #a3927e;
        font-size: 15px;
        height: 460px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 18px;
    }
    .lead-empty-icon {
        width: 88px;
        height: 88px;
        border-radius: 50%;
        background: var(--brown-100);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .lead-empty-state p {
        margin: 0;
        max-width: 220px;
        line-height: 1.4;
    }
    .detail-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--brown-200);
    }
    .detail-header h3 {
        margin: 0;
        font-family: 'Poppins', 'Inter', sans-serif;
    }

    /* ---------- Badges ---------- */
    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-left: 6px;
        border: 1px solid transparent;
    }
    .badge-hot { background: #fbe1dc; color: #c0392b; border-color: #f3c4bb; }
    .badge-warm { background: #faf0d7; color: #b7791f; border-color: #f0dfa8; }
    .badge-new { background: var(--brown-100); color: var(--brown-500); border-color: var(--brown-300); }
    .badge-cold { background: #e3ede8; color: #2f6f4f; border-color: #cbe0d5; }

    /* ---------- CSV import results ---------- */
    .import-complete-banner {
        background: #e3ede8;
        color: #2f6f4f;
        border: 1px solid #cbe0d5;
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 600;
        margin: 4px 0 16px 0;
    }
    .import-results-wrap {
        background: #ffffff;
        border: 1px solid var(--brown-200);
        border-radius: 14px;
        overflow: hidden;
        margin-top: 4px;
    }
    .import-results-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13.5px;
    }
    .import-results-table th {
        text-align: left;
        background: var(--brown-50);
        color: #a3927e;
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 10px 16px;
        border-bottom: 1px solid var(--brown-200);
    }
    .import-results-table td {
        padding: 10px 16px;
        border-bottom: 1px solid var(--brown-100);
        color: var(--brown-800);
        vertical-align: middle;
    }
    .import-results-table tr:last-child td {
        border-bottom: none;
    }
    .import-results-table td .badge {
        margin-left: 0;
    }
    .import-detail-cell {
        color: #a3927e;
    }

    /* ---------- Leads directory table ---------- */
    .leads-directory-wrap {
        background: #ffffff;
        border: 1px solid var(--brown-200);
        border-radius: 14px;
        overflow: auto;
        max-height: 480px;
        margin-top: 4px;
    }
    .leads-directory-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13.5px;
        white-space: nowrap;
    }
    .leads-directory-table thead th {
        position: sticky;
        top: 0;
        z-index: 1;
        text-align: left;
        background: var(--brown-50);
        color: #a3927e;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 10px 16px;
        border-bottom: 1px solid var(--brown-200);
    }
    .leads-directory-table td {
        padding: 10px 16px;
        border-bottom: 1px solid var(--brown-100);
        color: var(--brown-800);
        vertical-align: middle;
    }
    .leads-directory-table tr:last-child td {
        border-bottom: none;
    }
    .leads-directory-table tr:hover td {
        background: var(--brown-50);
    }
    .leads-directory-table td .badge {
        margin-left: 0;
    }
    .leads-dir-id {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-weight: 700;
        color: var(--brown-500);
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #e0c9ac !important;
        background: #ffffff;
        color: #8a4b1f;
        transition: all 0.12s ease;
    }
    .stButton > button:hover {
        background: #b5651d;
        color: white;
        border-color: #b5651d !important;
        box-shadow: 0 4px 12px rgba(181, 101, 29, 0.28);
        transform: translateY(-1px);
    }
    div[data-testid="stFormSubmitButton"] button {
        background: #b5651d !important;
        border: none !important;
    }
    div[data-testid="stFormSubmitButton"] button p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: #8a4b1f !important;
    }
    .stButton > button:disabled {
        background: #f1e6da !important;
        border-color: #ece3d8 !important;
        opacity: 1 !important;
    }
    .stButton > button:disabled p {
        color: #b5651d !important;
        font-weight: 700 !important;
    }

    /* ---------- Inputs ---------- */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"] {
        background-color: #ffffff !important;
        color: #3d2817 !important;
        border: 1px solid #e8ddd0 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #b5651d !important;
        box-shadow: 0 0 0 2px rgba(181, 101, 29, 0.12) !important;
    }

    /* ---------- Headings & body text ---------- */
    .stApp, .stApp p, .stApp label, .stApp span {
        color: #3d2817;
    }
    h1, h2, h3, h4, h5 {
        color: #4a2e1a !important;
        font-weight: 700 !important;
    }

    /* ---------- Alert / Confirmation banners ---------- */
    .duplicate-alert {
        background: #fdf1e0;
        border-left: 5px solid #d68910;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .duplicate-alert h4 {
        margin: 0 0 8px 0;
        color: #8a5a00;
    }
    .duplicate-alert p {
        margin: 2px 0;
        color: #5c3a00;
    }

    /* ---------- Streamlit native alert boxes (info/success/warning/error) ---------- */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.04);
        padding: 14px 16px !important;
    }

    /* ---------- Metric ---------- */
    div[data-testid="stMetric"] {
        background: var(--brown-50);
        border: 1px solid var(--brown-200);
        border-radius: 14px;
        padding: 14px 18px;
    }
    div[data-testid="stMetricValue"] {
        color: var(--brown-600) !important;
        font-family: 'Poppins', 'Inter', sans-serif;
    }
    div[data-testid="stMetricLabel"] {
        color: #8a7563 !important;
    }

    /* ---------- Progress bar ---------- */
    div[data-testid="stProgress"] div[role="progressbar"] > div {
        background: linear-gradient(90deg, var(--brown-400), var(--brown-600)) !important;
    }
    div[data-testid="stProgress"] div[role="progressbar"] {
        background: var(--brown-100) !important;
    }

    /* ---------- Card eyebrow label (small category text above a panel title) ---------- */
    .eyebrow-label {
        font-size: 12.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--brown-500);
        margin-bottom: 2px;
    }
    .card-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: var(--brown-800);
        margin-bottom: 14px;
    }

    /* ---------- Conversations tab output formatting ---------- */
    .insight-list {
        margin: 0;
        padding-left: 20px;
    }
    .insight-list li {
        color: var(--brown-900);
        font-size: 14.5px;
        line-height: 1.7;
    }
    .action-item {
        background: var(--brown-50);
        border: 1px solid var(--brown-200);
        border-radius: 10px;
        padding: 9px 14px;
        margin-bottom: 6px;
        font-size: 14.5px;
        color: var(--brown-900);
    }
    .info-row {
        display: flex;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid var(--brown-200);
        font-size: 14.5px;
    }
    .info-row:last-child { border-bottom: none; }
    .info-key {
        min-width: 100px;
        font-weight: 700;
        color: var(--brown-600);
    }
    .info-value {
        color: var(--brown-900);
    }

    /* ---------- Outreach: Preview Email card ---------- */
    .email-preview-card {
        background: #ffffff;
        border: 1px solid var(--brown-200);
        border-radius: 12px;
        padding: 18px 20px;
        margin: 4px 0 18px 0;
        box-shadow: 0 4px 14px rgba(74, 46, 26, 0.06);
    }
    .email-preview-row {
        font-size: 13.5px;
        color: var(--brown-900);
        padding: 4px 0;
        border-bottom: 1px solid var(--brown-100);
    }
    .email-preview-row span {
        display: inline-block;
        min-width: 64px;
        font-weight: 700;
        color: var(--brown-500);
        margin-right: 6px;
    }
    .email-preview-body {
        margin-top: 12px;
        font-size: 14px;
        line-height: 1.7;
        color: var(--brown-900);
        white-space: normal;
    }

    /* ---------- Outreach: numbered section badges ("1 Select Lead" etc.) ---------- */
    .section-num-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }
    .section-num-badge {
        width: 24px;
        height: 24px;
        min-width: 24px;
        border-radius: 50%;
        background: var(--brown-700);
        color: #ffffff;
        font-size: 12.5px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Poppins', 'Inter', sans-serif;
    }
    .section-num-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 16.5px;
        font-weight: 700;
        color: var(--brown-800);
    }
    /* Icon variant (Lead Scoring section headers) — no circle background,
       just the icon glyph itself. */
    .section-num-badge.icon-badge {
        width: auto;
        height: auto;
        min-width: 0;
        border-radius: 0;
        background: transparent;
        color: var(--brown-700);
        font-size: 19px;
    }

    /* ---------- Outreach: Select Lead card ---------- */
    .lead-select-card {
        display: flex;
        align-items: center;
        gap: 14px;
        background: #ffffff;
        border: 1px solid var(--brown-200);
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0 14px 0;
    }
    .lead-select-avatar {
        width: 46px;
        height: 46px;
        min-width: 46px;
        border-radius: 50%;
        background: var(--brown-100);
        color: var(--brown-600);
        font-weight: 700;
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .lead-select-info { flex: 1; min-width: 0; }
    .lead-select-name {
        font-size: 15px;
        font-weight: 700;
        color: var(--brown-900);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .lead-select-sub {
        font-size: 12.5px;
        color: var(--brown-600);
        margin-top: 1px;
    }
    .lead-select-email {
        font-size: 12px;
        color: #a3927e;
        margin-top: 1px;
    }
    .lead-score-pill {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 46px;
        border-radius: 12px;
        padding: 5px 10px;
        font-size: 16px;
        font-weight: 800;
        font-family: 'Poppins', 'Inter', sans-serif;
        line-height: 1.1;
    }
    .lead-score-pill span {
        font-size: 9.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .score-pill-high { background: #e3ede8; color: #2f6f4f; }
    .score-pill-mid { background: #faf0d7; color: #b7791f; }
    .score-pill-low { background: #fbe1dc; color: #c0392b; }

    /* ---------- Outreach: field labels above custom widgets ---------- */
    .field-label {
        font-size: 13.5px;
        font-weight: 700;
        color: var(--brown-700);
        margin-bottom: 4px;
    }

    /* ---------- Outreach: pain point / business goal chip rows ---------- */
    div[class*="st-key-pain_chip_row_"],
    div[class*="st-key-goal_chip_row_"] {
        margin-bottom: 4px;
    }
    /* Streamlit nests each st.button() as its own block inside an inner
       stVerticalBlock — that's the element that actually needs to become
       a wrapping flex row, not the outer st-key-* wrapper itself. */
    div[class*="st-key-pain_chip_row_"] div[data-testid="stVerticalBlock"],
    div[class*="st-key-goal_chip_row_"] div[data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
        row-gap: 6px !important;
    }
    div[class*="st-key-pain_chip_row_"] div[data-testid="stElementContainer"],
    div[class*="st-key-goal_chip_row_"] div[data-testid="stElementContainer"] {
        width: auto !important;
        flex: 0 0 auto !important;
    }
    div[class*="st-key-pain_chip_row_"] div[data-testid="stButton"],
    div[class*="st-key-goal_chip_row_"] div[data-testid="stButton"] {
        width: auto !important;
    }
    div[class*="st-key-pain_chip_row_"] button,
    div[class*="st-key-goal_chip_row_"] button {
        background: var(--brown-50) !important;
        border: 1px solid var(--brown-300) !important;
        color: var(--brown-700) !important;
        border-radius: 999px !important;
        padding: 2px 12px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        white-space: nowrap;
        line-height: 1.6 !important;
        min-height: unset !important;
    }
    div[class*="st-key-pain_chip_row_"] button:hover,
    div[class*="st-key-goal_chip_row_"] button:hover {
        background: #fbe1dc !important;
        border-color: #f3c4bb !important;
        color: #c0392b !important;
    }

    /* ---------- Outreach: empty state before an email has been generated ---------- */
    .empty-email-state {
        background: #ffffff;
        border: 1px dashed var(--brown-300);
        border-radius: 14px;
        padding: 40px 24px;
        text-align: center;
        color: var(--brown-600);
        font-size: 14px;
    }

    /* =========================================================
       Outreach tab v2 — matches the "Select Lead / Personalization
       Inputs / AI Generated Email" reference layout: three distinct,
       generously-padded white cards that never visually merge.
       ========================================================= */

    /* ---------- Card shells (Select Lead / Personalization / Generate Mail / AI email) ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-select_lead_card,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-personalization_card,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-generate_mail_card,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-ai_email_card {
        padding: 22px 24px 32px 24px !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 3px rgba(74, 46, 26, 0.05);
    }
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-select_lead_card [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-personalization_card [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-generate_mail_card [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"],
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-ai_email_card [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {
        padding-left: 2px;
        padding-right: 2px;
    }

    /* ---------- Card header row (icon + title), used by the AI Generated Email card ---------- */
    .oc-card-header {
        display: flex;
        align-items: center;
        gap: 9px;
        margin: 2px 0 12px 0;
    }
    .oc-card-icon {
        font-size: 17px;
        line-height: 1;
    }
    .oc-card-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 16.5px;
        font-weight: 700;
        color: var(--brown-800);
    }

    /* ---------- Numbered step header (icon box + "N. Title" + subtitle) ---------- */
    .oc-step-head {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin: 2px 0;
    }
    .oc-icon-box {
        width: 44px;
        height: 44px;
        min-width: 44px;
        border-radius: 12px;
        background: var(--brown-100);
        color: var(--brown-600);
        font-size: 19px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .oc-step-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: var(--brown-900);
        line-height: 1.3;
        margin-bottom: 2px;
    }
    .oc-step-subtitle {
        font-size: 13px;
        color: #a3927e;
        line-height: 1.3;
    }
    .oc-step-divider {
        border: none;
        border-top: 1px solid var(--brown-200);
        margin: 18px 0 16px 0;
    }

    /* Chevron (expand/collapse) buttons on step-card headers */
    div[class*="st-key-chevron_select_lead"] button,
    div[class*="st-key-chevron_personalization"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--brown-600) !important;
        font-size: 17px !important;
        padding: 6px 10px !important;
        min-height: unset !important;
    }
    div[class*="st-key-chevron_select_lead"] button:hover,
    div[class*="st-key-chevron_personalization"] button:hover {
        background: var(--brown-50) !important;
        border-radius: 8px !important;
    }

    /* ---------- Select Lead: avatar + dropdown row ---------- */
    .st-key-select_lead_card div[data-testid="stHorizontalBlock"]:has(.oc-lead-avatar) {
        align-items: center;
    }
    .oc-lead-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--brown-100);
        color: var(--brown-600);
        font-weight: 700;
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 14.5px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 2px;
    }
    .st-key-select_lead_card .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid var(--brown-200) !important;
        border-radius: 12px !important;
        min-height: 54px !important;
        padding: 6px 14px !important;
        box-shadow: none !important;
    }
    .st-key-select_lead_card .stSelectbox div[data-baseweb="select"] > div > div {
        color: var(--brown-900) !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
    }
    .st-key-select_lead_card .stSelectbox div[data-baseweb="select"]:focus-within > div {
        border-color: var(--brown-500) !important;
        box-shadow: 0 0 0 2px rgba(181, 101, 29, 0.12) !important;
    }

    /* ---------- Personalization Inputs: bordered box dropdowns + field labels ---------- */
    .pi-label {
        font-size: 13.5px;
        font-weight: 700;
        color: var(--brown-900);
        margin-bottom: 6px;
    }
    .st-key-personalization_card .stSelectbox {
        margin-bottom: 4px;
    }
    .st-key-personalization_card .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid var(--brown-200) !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        padding: 4px 12px !important;
        min-height: 46px !important;
    }
    .st-key-personalization_card .stSelectbox div[data-baseweb="select"] > div > div {
        color: var(--brown-900) !important;
        font-weight: 500 !important;
        font-size: 14.5px !important;
        padding-left: 0 !important;
    }
    .st-key-personalization_card .stSelectbox div[data-baseweb="select"]:focus-within > div {
        border-color: var(--brown-500) !important;
        box-shadow: 0 0 0 2px rgba(181, 101, 29, 0.12) !important;
    }
    .st-key-personalization_card .stSelectbox div[data-baseweb="select"] svg {
        fill: var(--brown-400) !important;
    }
    .st-key-personalization_card [data-testid="stCheckbox"] label p {
        font-size: 13.5px !important;
        color: var(--brown-800) !important;
    }
    .st-key-personalization_card [data-testid="stCheckbox"] {
        margin-bottom: 8px;
    }
    .st-key-personalization_card [data-testid="stCheckbox"] span[aria-checked="true"] {
        background-color: var(--brown-500) !important;
        border-color: var(--brown-500) !important;
    }
    .st-key-personalization_card [data-testid="stCheckbox"] span {
        border-color: var(--brown-300);
    }

    /* ---------- AI Generated Email: To row, Subject label, body box ---------- */
    .oc-to-row {
        display: flex;
        gap: 10px;
        font-size: 14px;
        color: var(--brown-900);
        padding: 4px 0 14px 0;
    }
    .oc-to-row span {
        font-weight: 700;
        color: var(--brown-600);
        min-width: 28px;
    }
    .oc-field-label-strong {
        font-size: 13.5px;
        font-weight: 700;
        color: var(--brown-800);
        margin-bottom: 4px;
    }
    .st-key-ai_email_card .stTextInput {
        margin-bottom: 12px;
    }
    .oc-email-body-box {
        background: #ffffff;
        border: 1px solid var(--brown-200);
        border-radius: 10px;
        padding: 16px 18px;
        min-height: 220px;
        font-size: 14.5px;
        line-height: 1.75;
        color: var(--brown-900);
    }
    .st-key-ai_email_card .stTextArea textarea {
        min-height: 220px;
        font-size: 14.5px;
        line-height: 1.75;
        background: #ffffff !important;
        color: var(--brown-900) !important;
        border: 1px solid var(--brown-200) !important;
        border-radius: 10px !important;
        padding: 16px 18px !important;
    }
    /* Disabled = "display" state: browsers grey/fade disabled textareas by
       default (lower opacity, muted text-fill). Override that so it reads
       exactly like normal, non-editable body text rather than a greyed-out
       form field. */
    .st-key-ai_email_card .stTextArea textarea:disabled {
        background: #ffffff !important;
        color: var(--brown-900) !important;
        -webkit-text-fill-color: var(--brown-900) !important;
        opacity: 1 !important;
        cursor: default !important;
        border-color: var(--brown-200) !important;
        resize: none !important;
    }
    .st-key-ai_email_card .stTextArea textarea:not(:disabled):focus {
        border-color: var(--brown-500) !important;
        box-shadow: 0 0 0 2px rgba(181, 101, 29, 0.12) !important;
    }

    /* ---------- Main-content primary buttons (Generate AI Email / Send Email) ---------- */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, var(--brown-500) 0%, var(--brown-700) 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(181, 101, 29, 0.28) !important;
    }
    div[data-testid="stButton"] button[kind="primary"] p {
        color: #ffffff !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--brown-600) 0%, var(--brown-800) 100%) !important;
        transform: translateY(-1px);
    }
    div[data-testid="stButton"] button[kind="primary"]:disabled {
        background: #f1e6da !important;
        color: #b5651d !important;
        box-shadow: none !important;
    }

    /* ---------- Score gauge (SVG ring, Outreach / Scoring / Company Intel tabs) ---------- */
    .score-gauge-outer {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        margin: 10px 0 18px 0;
    }
    .score-gauge-wrap {
        position: relative;
        margin: 0 auto;
    }
    .score-gauge-wrap svg {
        display: block;
        filter: drop-shadow(0 8px 18px rgba(74, 46, 26, 0.14));
    }
    .score-gauge-center {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .score-gauge-num {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 36px;
        font-weight: 800;
        color: var(--brown-900);
        line-height: 1;
    }
    .score-gauge-sub {
        font-size: 11.5px;
        color: #a3927e;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-top: 3px;
        text-transform: uppercase;
    }
    .score-gauge-label {
        text-align: center;
        margin-top: 10px;
        display: inline-block;
        padding: 6px 18px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.01em;
    }
    .score-gauge-label.tier-high {
        background: #e3f3e9;
        color: #2f6f4f;
        border: 1px solid #bfe2cd;
    }
    .score-gauge-label.tier-mid {
        background: #faf0d7;
        color: #a3691a;
        border: 1px solid #f0dfa8;
    }
    .score-gauge-label.tier-low {
        background: #fbe1dc;
        color: #c0392b;
        border: 1px solid #f3c4bb;
    }
    .conversion-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13.5px;
        color: #8a7563;
        margin-bottom: 4px;
    }
    .conversion-pct {
        font-weight: 700;
        color: var(--brown-700);
    }

    /* ---------- Company Intelligence: card headers (icon + title) ---------- */
    .intel-card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }
    .intel-card-icon {
        width: 34px;
        height: 34px;
        min-width: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        background: var(--brown-50);
    }
    .intel-card-icon.score { background: #fdeee0; }
    .intel-card-icon.snapshot { background: #e7ebf1; }
    .intel-card-icon.conversion { background: #e3ede8; }
    .intel-card-icon.insight { background: #eef2fb; }
    .intel-card-icon.opportunity { background: #faf0d7; }
    .intel-card-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-weight: 700;
        font-size: 15px;
        color: var(--brown-800);
    }
    .intel-card-body {
        font-size: 14px;
        line-height: 1.7;
        color: var(--brown-900);
    }
    .intel-card-sub {
        font-size: 12px;
        color: #a3927e;
        margin-top: -10px;
        margin-bottom: 14px;
    }

    /* ---------- Engagement level badge (auto-colored pill) ---------- */
    .engagement-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12.5px;
        font-weight: 700;
        letter-spacing: 0.01em;
        line-height: 1.5;
    }
    .engagement-badge.level-high {
        background: #e3f3e9;
        color: #2f6f4f;
        border: 1px solid #bfe2cd;
    }
    .engagement-badge.level-medium {
        background: #faf0d7;
        color: #a3691a;
        border: 1px solid #f0dfa8;
    }
    .engagement-badge.level-low {
        background: #fbe1dc;
        color: #c0392b;
        border: 1px solid #f3c4bb;
    }
    .engagement-badge.level-unknown {
        background: var(--brown-100);
        color: #a3927e;
        border: 1px solid var(--brown-200);
    }

    /* ---------- Conversion probability gradient bar ---------- */
    .conv-bar-wrap {
        margin: 4px 0 2px 0;
    }
    .conv-bar-pct {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 32px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 12px;
    }
    .conv-bar-pct.tier-high { color: #2f9e5f; }
    .conv-bar-pct.tier-mid { color: #c98a26; }
    .conv-bar-pct.tier-low { color: #c0392b; }
    .conv-bar-track {
        position: relative;
        height: 10px;
        border-radius: 999px;
        background: linear-gradient(90deg, #f0897a 0%, #f0c674 50%, #5fd68a 100%);
        margin: 6px 2px 0 2px;
    }
    .conv-bar-marker {
        position: absolute;
        top: 50%;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #ffffff;
        border: 3px solid var(--brown-800);
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 6px rgba(74, 46, 26, 0.3);
    }
    .conv-bar-scale {
        display: flex;
        justify-content: space-between;
        font-size: 10.5px;
        color: #a3927e;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }
    .conv-bar-tier-label {
        text-align: center;
        margin-top: 14px;
        display: inline-block;
        padding: 5px 16px;
        border-radius: 999px;
        font-size: 12.5px;
        font-weight: 700;
    }
    .conv-bar-tier-label.tier-high {
        background: #e3f3e9;
        color: #2f6f4f;
        border: 1px solid #bfe2cd;
    }
    .conv-bar-tier-label.tier-mid {
        background: #faf0d7;
        color: #a3691a;
        border: 1px solid #f0dfa8;
    }
    .conv-bar-tier-label.tier-low {
        background: #fbe1dc;
        color: #c0392b;
        border: 1px solid #f3c4bb;
    }

    /* ---------- Company Intelligence: bordered card containers ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_score_card,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_snapshot_card,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_conversion_card,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_insight_card,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_opportunity_card {
        box-shadow: 0 1px 2px rgba(74, 46, 26, 0.05);
        transition: all 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_score_card:hover,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_snapshot_card:hover,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_conversion_card:hover,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_insight_card:hover,
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-intel_opportunity_card:hover {
        border-color: var(--brown-300) !important;
        box-shadow: 0 10px 22px rgba(74, 46, 26, 0.08);
    }

    /* ---------- Company Intelligence: equal-height cards per row ----------
       Scoped (via :has) to only the two rows that hold our intel cards, so
       every card in a row matches the height of the tallest card in that
       row instead of hugging its own (shorter) content.

       This uses a generic "> div" chain (instead of hard-coding every
       Streamlit internal testid) so it keeps working even if a future
       Streamlit version adds/removes a wrapper level between stColumn and
       the actual bordered card div. */
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_score_card),
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_insight_card) {
        display: flex !important;
        align-items: stretch !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_score_card) > div[data-testid="stColumn"],
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_insight_card) > div[data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
        height: auto !important;
    }

    /* Walk down up to 3 generic wrapper levels, forcing each to stretch
       to the height handed down by its flex parent. */
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_score_card) > div[data-testid="stColumn"] > div,
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_insight_card) > div[data-testid="stColumn"] > div,
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_score_card) > div[data-testid="stColumn"] > div > div,
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_insight_card) > div[data-testid="stColumn"] > div > div,
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_score_card) > div[data-testid="stColumn"] > div > div > div,
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_insight_card) > div[data-testid="stColumn"] > div > div > div {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        width: 100% !important;
        min-height: 0 !important;
    }

    /* Whichever level actually is the bordered card, force it to fill
       the full stretched height and lay its own content out top-to-bottom. */
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_score_card) div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_insight_card) div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        height: 100% !important;
    }

    /* The inner content block of the card (header + body) should not
       stretch itself full height - just stack naturally from the top. */
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_score_card) div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"]:has(.st-key-intel_insight_card) div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
        height: 100% !important;
    }

    /* ---------- CRM sync log feed (Conversations tab) ---------- */
    .crm-log-item {
        background: var(--brown-50);
        border: 1px solid var(--brown-200);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .crm-log-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
    }
    .crm-log-name {
        font-size: 13.5px;
        font-weight: 700;
        color: var(--brown-800);
    }
    .crm-log-meta {
        font-size: 12.5px;
        color: #a3927e;
        margin-top: 3px;
    }

    /* ---------- Dashboard: performance metric tiles (m1-m5) ---------- */
    .stat-card.m1::before, .stat-card.m1 .stat-value { color: var(--brown-500); }
    .stat-card.m1::before { background: var(--brown-500); }
    .stat-card.m1 .stat-icon { background: #fdeee0; }

    .stat-card.m2::before { background: #b5322c; }
    .stat-card.m2 .stat-value { color: #b5322c; }
    .stat-card.m2 .stat-icon { background: #fbe1dc; }

    .stat-card.m3::before { background: #2f6f4f; }
    .stat-card.m3 .stat-value { color: #2f6f4f; }
    .stat-card.m3 .stat-icon { background: #e3ede8; }

    .stat-card.m4::before { background: #8a5a00; }
    .stat-card.m4 .stat-value { color: #8a5a00; }
    .stat-card.m4 .stat-icon { background: #faf0d7; }

    .stat-card.m5::before { background: #5c6f8a; }
    .stat-card.m5 .stat-value { color: #5c6f8a; }
    .stat-card.m5 .stat-icon { background: #e7ebf1; }

    /* ---------- Dashboard: pipeline value + kanban board ---------- */
    .pipeline-value-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 16px;
    }
    .pipeline-value-chip {
        background: var(--brown-50);
        border: 1px solid var(--brown-300);
        color: var(--brown-700);
        font-weight: 700;
        font-size: 14px;
        padding: 8px 16px;
        border-radius: 999px;
    }
    .pipeline-col-header {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--brown-700);
        border-bottom: 2px solid var(--brown-300);
        padding-bottom: 8px;
        margin-bottom: 10px;
    }
    .pipeline-col-count {
        color: #a3927e;
        font-weight: 600;
        margin-left: 4px;
    }
    .pipeline-card {
        background: #ffffff;
        border: 1px solid var(--brown-200);
        border-left: 3px solid var(--brown-400);
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    .pipeline-card-name {
        font-size: 13.5px;
        font-weight: 700;
        color: var(--brown-900);
    }
    .pipeline-card-amount {
        font-size: 12.5px;
        color: var(--brown-600);
        margin-top: 3px;
    }

    /* ---------- Login / Signup page (split brand + form panel) ---------- */
    .login-page {
        padding-top: 36px;
    }
    .st-key-login_shell {
        max-width: 1000px;
        margin: 0 auto;
        background: rgba(255, 255, 255, 0.16);
        border-radius: 26px;
        overflow: hidden;
        box-shadow: 0 24px 70px rgba(74, 46, 26, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(22px) saturate(140%);
        -webkit-backdrop-filter: blur(22px) saturate(140%);
    }
    .st-key-login_shell [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: stretch !important;
    }
    .st-key-login_shell [data-testid="stColumn"] {
        display: flex;
        flex-direction: column;
    }

    /* Left: brand / marketing panel */
    .login-brand-panel {
        background: linear-gradient(160deg, rgba(251, 241, 228, 0.35) 0%, rgba(241, 230, 218, 0.3) 55%, rgba(232, 221, 208, 0.22) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.35);
        min-height: 580px;
        height: 100%;
        padding: 52px 42px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .login-brand-avatar {
        width: 54px;
        height: 54px;
        border-radius: 16px;
        background: linear-gradient(135deg, var(--gold-500) 0%, var(--gold-700) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--ink-900);
        font-weight: 800;
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 18px;
        margin-bottom: 24px;
        box-shadow: 0 10px 26px rgba(224, 168, 62, 0.32);
    }
    .login-brand-panel h1 {
        color: var(--brown-900) !important;
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 27px;
        font-weight: 700;
        margin: 0 0 10px 0;
        letter-spacing: -0.01em;
    }
    .login-brand-tag {
        color: var(--brown-600);
        font-size: 14.5px;
        line-height: 1.55;
        margin: 0 0 30px 0;
        max-width: 340px;
    }
    .login-brand-features {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    .login-brand-features li {
        color: var(--brown-800);
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .login-brand-features li .dot {
        width: 6px; height: 6px; min-width: 6px;
        border-radius: 50%;
        background: var(--gold-600);
    }

    /* Right: form panel */
    .st-key-login_form_panel {
        padding: 52px 48px !important;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    .login-form-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: var(--brown-800);
        margin-bottom: 4px;
    }
    .login-form-subtitle {
        font-size: 14px;
        color: #a3927e;
        margin-bottom: 22px;
    }
    .login-divider {
        display: flex;
        align-items: center;
        text-align: center;
        color: #c9b8a5;
        font-size: 12.5px;
        margin: 16px 0;
    }
    .login-divider::before,
    .login-divider::after {
        content: "";
        flex: 1;
        border-bottom: 1px solid var(--brown-200);
    }
    .login-divider span {
        padding: 0 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .login-footer {
        text-align: center;
        font-size: 14px;
        color: #8a7563;
        margin: 18px 0 8px 0;
    }

    /* Glass treatment for controls inside the login/signup card, so the
       background image shows through instead of sitting behind a solid
       white box. */
    .st-key-login_form_panel .stTextInput input,
    .st-key-login_form_panel .stTextArea textarea,
    .st-key-login_form_panel div[data-baseweb="input"],
    .st-key-login_form_panel div[data-baseweb="base-input"] {
        background-color: rgba(255, 255, 255, 0.45) !important;
        border: 1px solid rgba(232, 221, 208, 0.7) !important;
    }
    .st-key-login_form_panel .stButton > button {
        background: rgba(255, 255, 255, 0.35) !important;
        border: 1px solid rgba(224, 201, 172, 0.8) !important;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
    }
    .st-key-login_form_panel .stButton > button:hover {
        background: #b5651d !important;
    }
    .st-key-login_form_panel div[data-testid="stFormSubmitButton"] button {
        box-shadow: 0 10px 26px rgba(181, 101, 29, 0.28) !important;
    }

    /* =========================================================
       Lead Scoring & Recommendation Engine (redesigned)
       ========================================================= */

    /* ---------- Section 2: Score breakdown metric rows ---------- */
    .metric-row { box-sizing: border-box; margin-bottom: 20px; }
    .metric-row:last-child { margin-bottom: 4px; }
    .metric-row-top {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }
    .metric-icon { font-size: 15px; }
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--brown-800);
    }
    .metric-row-bottom {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .metric-bar-track {
        flex: 1;
        height: 8px;
        border-radius: 6px;
        background: var(--brown-200);
        overflow: hidden;
    }
    .metric-bar-fill {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, var(--brown-500), var(--brown-600));
    }
    .metric-value {
        min-width: 58px;
        text-align: right;
        font-size: 13px;
        font-weight: 700;
        color: var(--brown-700);
    }

    /* ---------- Section 3: AI Recommendation box ---------- */
    .recommendation-box {
        box-sizing: border-box;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        background: var(--brown-50);
        border: 1px solid var(--brown-200);
        border-radius: 14px;
        padding: 20px;
        height: auto;
        width: 100%;
    }
    .recommendation-icon {
        width: 40px;
        height: 40px;
        min-width: 40px;
        border-radius: 50%;
        background: #fdeee0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .recommendation-text {
        font-size: 14.5px;
        line-height: 1.7;
        color: var(--brown-900);
    }

    /* ---------- Section 4: Best Action cards ---------- */
    /* Equal-height cards via a pure flex-grow chain. Instead of naming
       every Streamlit wrapper div by data-testid (fragile — a single
       unlisted wrapper in between silently breaks the stretch), target
       every ancestor of .best-action-card with :has() and turn it into
       a flex column that fills its parent. That reliably carries the
       stretch all the way from the row down to the card itself, so all
       three cards match the tallest one's height with even padding —
       without affecting the icon/pill, which aren't ancestors of the
       card and so never match this selector. */
    div[data-testid="stHorizontalBlock"]:has(.best-action-card) {
        align-items: stretch !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.best-action-card) div[data-testid="stColumn"]:has(.best-action-card) {
        display: flex !important;
        flex-direction: column !important;
        height: auto !important;
        min-height: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.best-action-card) div[data-testid="stColumn"]:has(.best-action-card) div:has(.best-action-card) {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        min-height: 0 !important;
        width: 100%;
    }
    .best-action-card {
        box-sizing: border-box;
        background: #ffffff;
        border: 1px solid var(--brown-200);
        border-radius: 14px;
        padding: 20px;
        width: 100%;
        flex: 1 1 auto;
        min-height: 0;
        display: flex;
        flex-direction: column;
        overflow: visible;
    }
    .best-action-icon {
        width: 40px;
        height: 40px;
        min-height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 17px;
        margin-bottom: 12px;
        flex: 0 0 auto;
    }
    .best-action-icon.green { background: #dff3e8; color: #2f9e5f; }
    .best-action-icon.amber { background: #faf0d7; color: #b7791f; }
    .best-action-icon.red { background: #fbe1dc; color: #c0392b; }
    .best-action-title {
        font-family: 'Poppins', 'Inter', sans-serif;
        font-weight: 700;
        font-size: 15px;
        color: var(--brown-800);
        margin-bottom: 6px;
        flex: 0 0 auto;
    }
    .best-action-desc {
        font-size: 13.5px;
        line-height: 1.6;
        color: #8a7563;
        margin-bottom: 14px;
        flex: 1 1 auto;
    }
    .action-priority-pill {
        display: inline-block;
        align-self: flex-start;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        flex: 0 0 auto;
        margin-top: auto;
    }
    .action-priority-pill.priority-high { background: #dff3e8; color: #2f9e5f; }
    .action-priority-pill.priority-medium { background: #faf0d7; color: #b7791f; }
    .action-priority-pill.priority-low { background: #fbe1dc; color: #c0392b; }

    /* =========================================================
       MOBILE RESPONSIVE LAYER
       Everything below only kicks in on phone/small-tablet
       viewports. Desktop layout above is untouched.
       ========================================================= */
    @media (max-width: 768px) {
        html, body, [class*="css"] {
            font-size: 15px;
        }

        /* Tighter outer page padding so content isn't cramped
           against the screen edges. */
        .block-container {
            padding-top: 1rem !important;
            padding-left: 0.9rem !important;
            padding-right: 0.9rem !important;
            padding-bottom: 1.25rem !important;
        }

        /* Stack every side-by-side Streamlit column layout in the
           main content area into a single column. The sidebar is
           handled separately (see app.py) and is excluded here. */
        div[data-testid="stMain"] div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            row-gap: 12px !important;
            column-gap: 0 !important;
        }
        div[data-testid="stMain"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            flex: 1 1 100% !important;
            width: 100% !important;
            min-width: 100% !important;
        }

        /* Buttons and inputs get comfortably tappable and use the
           full available width by default on small screens. */
        .stButton > button {
            width: 100%;
            min-height: 44px;
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"], .stNumberInput input {
            min-height: 42px;
        }

        /* Tabs: allow horizontal scroll instead of squeezing/wrapping
           labels illegibly. */
        .stTabs [role="tablist"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch;
        }
        .stTabs [data-testid="stTab"] {
            flex: 0 0 auto !important;
        }

        /* Dataframes/tables scroll horizontally rather than overflowing
           the viewport. */
        div[data-testid="stDataFrame"], div[data-testid="stTable"] {
            overflow-x: auto !important;
            max-width: 100vw;
        }

        /* Metric cards and KPI stat rows read better stacked full-width
           on a phone than squeezed into slivers. */
        div[data-testid="stMetric"] {
            width: 100% !important;
        }

        /* Score gauge shrinks a little so it never crowds the score
           card content next to it once stacked. */
        .score-gauge-wrap {
            max-width: 100%;
        }

        /* Sidebar brand text: keep it legible without pushing the
           narrower mobile drawer width. */
        .sidebar-brand-text h1 {
            font-size: 15px !important;
        }
        .sidebar-brand-text p {
            font-size: 11px !important;
        }

        /* Login / signup: the marketing side panel is a nice-to-have on
           desktop but eats the whole screen on mobile, so it gets
           dropped in favor of just the form. */
        .st-key-login_shell {
            max-width: 100% !important;
            border-radius: 18px !important;
            margin: 0 12px !important;
        }
        .login-brand-panel {
            display: none !important;
        }
        .login-page {
            padding-top: 16px !important;
        }

        /* Pipeline board: each stage becomes its own full-width stacked
           section instead of a cramped horizontal-scroll kanban, with a
           divider so consecutive stages don't visually run together. */
        div[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.pipeline-col-header) > div[data-testid="stColumn"] {
            border-top: 1px solid var(--brown-200);
            padding-top: 10px;
            margin-top: 6px;
        }
        div[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.pipeline-col-header) > div[data-testid="stColumn"]:first-child {
            border-top: none;
            padding-top: 0;
            margin-top: 0;
        }

        /* Two-pane "list + detail" views (e.g. Leads) stack with the
           list on top, matching the generic column-stacking rule above,
           but give the detail pane a bit of breathing room once it
           drops below the list. */
        div[data-testid="stMain"] div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
            margin-bottom: 0;
        }
    }

    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }
        html, body, [class*="css"] {
            font-size: 14px;
        }
    }
    </style>

    """, unsafe_allow_html=True)