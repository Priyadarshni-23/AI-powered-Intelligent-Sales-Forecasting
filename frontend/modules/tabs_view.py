import streamlit as st
from database import get_all_leads_full
from modules import leads_tab, generate_email, score_lead, summarize_call, analyze_company, crm_sync, pipeline_dashboard


def _module_header(title, subtitle):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <p class="section-subtitle">{subtitle}</p>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# 1. Lead Management & Prospect Database
# ------------------------------------------------------------------
def render_leads_tab():
    leads_tab.show()


# ------------------------------------------------------------------
# 1b. Add Lead (CSV Import / Manual Import)
# ------------------------------------------------------------------
def render_add_lead_tab():
    st.markdown('<div class="section-title" style="margin-bottom:0;">Add Lead</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-subtitle">Import leads in bulk from a CSV file, or add a single lead manually.</p>',
        unsafe_allow_html=True,
    )

    csv_tab, manual_tab = st.tabs(["CSV Import", "Manual Import"])

    with csv_tab:
        leads_tab._render_csv_upload()

    with manual_tab:
        leads_tab._render_add_lead_form()


# ------------------------------------------------------------------
# 2. Lead Intelligence & Company Analysis
# ------------------------------------------------------------------
def render_company_intel_tab():
    _module_header(
        "Lead Intelligence & Company Analysis",
        "Analyze company profiles, identify business needs and opportunities, "
        "and generate lead qualification scores.",
    )
    analyze_company.show()


# ------------------------------------------------------------------
# 3. AI Outreach Generation
# ------------------------------------------------------------------
def render_outreach_tab():
    _module_header(
        "AI Outreach Generation",
        "Generate personalized outreach emails and follow-ups that convert "
        "prospects into real meetings.",
    )
    generate_email.show()


# ------------------------------------------------------------------
# 4. Lead Scoring & Recommendation Engine
# ------------------------------------------------------------------
def render_scoring_tab():
    _module_header(
        "Lead Scoring & Recommendation Engine",
        "Predict conversion likelihood, assign qualification scores, and "
        "get next-best-action recommendations.",
    )
    score_lead.show()


# ------------------------------------------------------------------
# 5. Conversation Intelligence & CRM Integration
# ------------------------------------------------------------------
def render_conversations_tab():
    _module_header(
        "Conversation Intelligence & CRM Integration",
        "Summarize sales calls and meetings, extract action items, and "
        "sync activity with your CRM.",
    )
    col_crm, col_summary = st.columns(2)

    with col_crm:
        with st.container(border=True):
            crm_sync.show()

    with col_summary:
        with st.container(border=True):
            summarize_call.show()


# ------------------------------------------------------------------
# 6. Dashboard & Sales Analytics
# ------------------------------------------------------------------
def render_dashboard_tab():
    _module_header(
        "Dashboard & Sales Analytics",
        "Track lead performance, pipeline status, and outreach effectiveness "
        "in one place.",
    )

    # Fetched once and reused by both the stat cards below and the
    # pipeline board inside pipeline_dashboard.show() — a single source
    # of truth per render, so the two can never disagree with each
    # other, and every future status/stage added on the backend shows
    # up automatically without a frontend code change.
    try:
        leads = get_all_leads_full(limit=100)
    except Exception as e:
        st.error(f"Could not load leads for the dashboard: {e}")
        leads = []

    total_leads = len(leads)

    # Canonical stage order first (matches the pipeline board below),
    # then any other status value found in the data that isn't one of
    # the canonical stages — so a brand-new status never silently goes
    # uncounted and the cards always sum to the total.
    canonical_order = ["New", "Contacted", "Qualified", "Warm", "Hot", "Cold"]
    counts = {stage: 0 for stage in canonical_order}
    for lead in leads:
        status = lead.get("status") or "New"
        counts[status] = counts.get(status, 0) + 1

    color_cycle = ["c1", "c2", "c3", "c4", "c5"]
    stats = [("Total leads", total_leads, "c1")] + [
        (f"{stage} leads", count, color_cycle[i % len(color_cycle)])
        for i, (stage, count) in enumerate(counts.items())
    ]

    cols_per_row = 4
    for row_start in range(0, len(stats), cols_per_row):
        row_stats = stats[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, (label, value, color_class) in zip(cols, row_stats):
            with col:
                st.markdown(f"""
                    <div class="stat-card {color_class}">
                        <div class="stat-label">{label}</div>
                        <div class="stat-value">{value}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    pipeline_dashboard.show(leads=leads)


NAV_ITEMS = [
    ("leads", "Leads", "list_alt"),
    ("add_lead", "Add Lead", "person_add"),
    ("company", "Company Intelligence", "apartment"),
    ("outreach", "Outreach", "send"),
    ("scoring", "Lead Scoring", "track_changes"),
    ("conversations", "Conversations", "chat"),
    ("dashboard", "Dashboard", "dashboard"),
]

_RENDERERS = {
    "leads": render_leads_tab,
    "add_lead": render_add_lead_tab,
    "company": render_company_intel_tab,
    "outreach": render_outreach_tab,
    "scoring": render_scoring_tab,
    "conversations": render_conversations_tab,
    "dashboard": render_dashboard_tab,
}


def render(section):
    _RENDERERS.get(section, render_leads_tab)()


def show():
    if "active_section" not in st.session_state:
        st.session_state.active_section = "leads"
    render(st.session_state.active_section)