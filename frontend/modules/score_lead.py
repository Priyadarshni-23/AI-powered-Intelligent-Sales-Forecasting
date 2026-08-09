import html

import requests
import streamlit as st

from database import get_all_leads
from modules.gauge import render_score_gauge

API_BASE = "http://127.0.0.1:8000"


# ----------------------------------------------------------------------
# Backend calls
# ----------------------------------------------------------------------
def generate_lead_score(lead_id):
    """
    Calls the backend AI scoring API.
    Backend endpoint: POST /scoring/generate/{lead_id}
    """
    response = requests.post(f"{API_BASE}/scoring/generate/{lead_id}")

    if response.status_code != 200:
        try:
            error_detail = response.json()
        except Exception:
            error_detail = response.text

        raise Exception(
            f"Scoring API failed ({response.status_code}): {error_detail}"
        )

    return response.json()


# ----------------------------------------------------------------------
# Score breakdown (Engagement / Fit / Intent / Decision Readiness)
# ----------------------------------------------------------------------
def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def _sub_scores(result, qualification_score):
    """
    Prefers real numeric sub-scores from the backend
    (engagement_score / fit_score / intent_score / decision_readiness).
    Today's /scoring endpoint doesn't return those yet, so this falls
    back to a deterministic estimate built from what it *does* return
    (qualification_score, engagement_level, conversion_probability) so
    the breakdown isn't empty. Swap this out once the backend adds
    real per-dimension scores.
    """
    engagement_level = (result.get("engagement_level") or "").strip().lower()
    engagement_anchor = {"high": 80, "medium": 55, "low": 30}.get(engagement_level, 50)

    try:
        conversion_probability = float(result.get("conversion_probability") or 0)
    except (TypeError, ValueError):
        conversion_probability = 0.0

    engagement_score = result.get("engagement_score")
    if engagement_score is None:
        engagement_score = round(engagement_anchor * 0.7 + qualification_score * 0.3)

    fit_score = result.get("fit_score")
    if fit_score is None:
        fit_score = round(qualification_score * 0.9)

    intent_score = result.get("intent_score")
    if intent_score is None:
        intent_score = round(qualification_score * 0.5 + (conversion_probability * 100) * 0.5)

    decision_readiness = result.get("decision_readiness")
    if decision_readiness is None:
        decision_readiness = round(qualification_score)

    return [
        ("&#128172;", "Engagement Score", _clamp(int(engagement_score))),
        ("&#128188;", "Fit Score", _clamp(int(fit_score))),
        ("&#128200;", "Intent Score", _clamp(int(intent_score))),
        ("&#128100;", "Decision Readiness", _clamp(int(decision_readiness))),
    ]


def _metric_bar_html(icon, label, value):
    return f"""
    <div class="metric-row">
        <div class="metric-row-top">
            <span class="metric-icon">{icon}</span>
            <span class="metric-label">{html.escape(label)}</span>
        </div>
        <div class="metric-row-bottom">
            <div class="metric-bar-track">
                <div class="metric-bar-fill" style="width:{value}%;"></div>
            </div>
            <span class="metric-value">{value} / 100</span>
        </div>
    </div>
    """


# ----------------------------------------------------------------------
# Best actions
# ----------------------------------------------------------------------
def _best_actions(result):
    """
    Uses a backend-provided `best_actions` list if the API ever returns
    one. Otherwise builds three cards from what it returns today: the
    real `next_best_action` text as the top-priority card, plus two
    general sales-process follow-ups so the section isn't empty.
    """
    provided = result.get("best_actions")
    if isinstance(provided, list) and provided:
        return provided

    next_best_action = result.get("next_best_action") or "Follow up with this lead."

    return [
        {
            "icon": "&#128222;",
            "color": "green",
            "title": "Recommended Next Step",
            "description": next_best_action,
            "priority": "High",
        },
        {
            "icon": "&#128100;",
            "color": "amber",
            "title": "Identify Decision Maker",
            "description": "Identify the executive sponsor required for budget approval.",
            "priority": "Medium",
        },
        {
            "icon": "&#128196;",
            "color": "red",
            "title": "Share Case Studies",
            "description": "Share relevant case studies from similar organizations.",
            "priority": "Low",
        },
    ]


def _priority_class(priority):
    p = (priority or "").strip().lower()
    if p == "high":
        return "priority-high"
    if p == "medium":
        return "priority-medium"
    return "priority-low"


def _action_card_html(action):
    priority = action.get("priority", "Low")
    return f"""
    <div class="best-action-card">
        <div class="best-action-icon {action.get('color', 'amber')}">{action.get('icon', '&#9889;')}</div>
        <div class="best-action-title">{html.escape(action.get('title', ''))}</div>
        <div class="best-action-desc">{html.escape(action.get('description', ''))}</div>
        <span class="action-priority-pill {_priority_class(priority)}">{html.escape(priority)} Priority</span>
    </div>
    """


def show():
    leads = get_all_leads()

    if not leads:
        st.info("No leads available. Please add a lead first.")
        return

    lead_options = {f"{lead[1]} ({lead[3]})": lead for lead in leads}
    option_labels = list(lead_options.keys())

    sel_key = "score_lead_select"
    current_label = st.session_state.get(sel_key)
    if current_label not in option_labels:
        current_label = option_labels[0]

    lead = lead_options[current_label]
    lead_id = lead[0]

    # -----------------------------------------------------------------
    # 1. Select Lead
    # -----------------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-num-row"><span class="section-num-badge icon-badge">&#128100;</span>'
            '<span class="section-num-title">Select Lead</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-subtitle" style="margin-top:-6px;">Choose a lead to analyze and score</p>',
            unsafe_allow_html=True,
        )

        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_label = st.selectbox(
                "Select a lead",
                option_labels,
                index=option_labels.index(current_label),
                key=sel_key,
                label_visibility="collapsed",
            )
        with col_btn:
            analyze_clicked = st.button(
                "✨ Analyze Lead",
                use_container_width=True,
                type="primary",
                key="analyze_lead_btn",
            )

    lead = lead_options[selected_label]
    lead_id = lead[0]

    # -----------------------------------------------------------------
    # Handle scoring trigger
    # -----------------------------------------------------------------
    if analyze_clicked:
        try:
            with st.spinner("AI is analyzing the lead..."):
                fresh_result = generate_lead_score(lead_id)
            st.session_state["score_lead_result_for"] = lead_id
            st.session_state["score_lead_result"] = fresh_result
            st.success("AI lead scoring completed successfully!")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the backend. Please make sure your "
                "FastAPI backend is running on http://127.0.0.1:8000."
            )
        except Exception as e:
            st.error(f"Failed to generate AI lead score: {e}")

    # Score / Recommendation / Best Actions only appear once this lead
    # has actually been analyzed in the current session — no silent
    # loading of a previously stored score.
    if st.session_state.get("score_lead_result_for") == lead_id:
        result = st.session_state.get("score_lead_result")
    else:
        result = None

    if not result:
        st.info("Click **Analyze Lead** above to generate the AI score, recommendation, and best actions.")
        return

    qualification_score = _clamp(int(result.get("qualification_score", 0)))
    recommendation = result.get("recommendation", "No recommendation available.")

    # -----------------------------------------------------------------
    # 2. Score
    # -----------------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-num-row"><span class="section-num-badge icon-badge">&#127919;</span>'
            '<span class="section-num-title">Score</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-subtitle" style="margin-top:-6px;">AI predicted conversion likelihood</p>',
            unsafe_allow_html=True,
        )

        gauge_col, metrics_col = st.columns([1, 1.5])

        with gauge_col:
            st.markdown(
                render_score_gauge(qualification_score, size=176),
                unsafe_allow_html=True,
            )

        with metrics_col:
            bars_html = "".join(
                _metric_bar_html(icon, label, value)
                for icon, label, value in _sub_scores(result, qualification_score)
            )
            st.markdown(bars_html, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 3. Recommendation
    # -----------------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-num-row"><span class="section-num-badge icon-badge">&#128161;</span>'
            '<span class="section-num-title">Recommendation</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-subtitle" style="margin-top:-6px;">What our AI suggests based on lead analysis</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="recommendation-box">
                <div class="recommendation-icon">&#10024;</div>
                <div class="recommendation-text">{html.escape(recommendation)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 4. Best Actions
    # -----------------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            '<div class="section-num-row"><span class="section-num-badge icon-badge">&#9889;</span>'
            '<span class="section-num-title">Best Actions</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-subtitle" style="margin-top:-6px;">Recommended actions to move this lead forward</p>',
            unsafe_allow_html=True,
        )

        actions = _best_actions(result)
        action_cols = st.columns(len(actions))
        for col, action in zip(action_cols, actions):
            with col:
                st.markdown(_action_card_html(action), unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
