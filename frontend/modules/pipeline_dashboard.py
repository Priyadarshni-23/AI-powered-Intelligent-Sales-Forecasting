import re
import requests
import streamlit as st
from database import get_all_leads_full

API_BASE = "http://127.0.0.1:8000"

PIPELINE_STAGES = ["New", "Contacted", "Qualified", "Warm", "Hot", "Cold"]


def _fetch_summary():
    response = requests.get(f"{API_BASE}/dashboard/summary", timeout=15)
    response.raise_for_status()
    return response.json()


def _parse_amount(value):
    if not value:
        return None
    digits = re.sub(r"[^\d.]", "", str(value))
    if not digits:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


def render_summary_metrics():
    try:
        summary = _fetch_summary()
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the backend. Please make sure your "
            "FastAPI backend is running on http://127.0.0.1:8000."
        )
        return
    except Exception as e:
        st.error(f"Could not load dashboard summary: {e}")
        return

    total_campaigns = summary.get("total_email_campaigns", 0)
    emails_sent = summary.get("emails_sent", 0)
    sent_label = (
        f"{emails_sent}/{total_campaigns}" if total_campaigns else str(emails_sent)
    )

    metrics = [
        ("Total Leads", summary.get("total_leads", 0), "m1"),
        ("Avg Lead Score", f"{summary.get('average_lead_score', 0):.0f}", "m2"),
        ("High-Priority Leads", summary.get("high_priority_leads", 0), "m3"),
        ("Emails Sent", sent_label, "m4"),
        ("Meetings Logged", summary.get("total_meetings", 0), "m5"),
        ("CRM Syncs", summary.get("total_crm_syncs", 0), "m6"),
    ]

    cols = st.columns(len(metrics))
    for col, (label, value, color_class) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="stat-card {color_class}">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value" style="font-size:24px;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_pipeline_board(leads=None):
    if leads is None:
        try:
            leads = get_all_leads_full(limit=100)
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the backend. Please make sure your "
                "FastAPI backend is running on http://127.0.0.1:8000."
            )
            return
        except Exception as e:
            st.error(f"Could not load pipeline data: {e}")
            return

    if not leads:
        st.markdown(
            '<p class="text-muted" style="font-size:14px;">No leads yet.</p>',
            unsafe_allow_html=True,
        )
        return

    # Total pipeline value: sum of parseable budget amounts, grouped by
    # currency since amounts aren't guaranteed to share one currency.
    totals_by_currency = {}
    for lead in leads:
        amount = _parse_amount(lead.get("budget_amount"))
        if amount is None:
            continue
        currency = (lead.get("budget_currency") or "").strip() or "Unspecified"
        totals_by_currency[currency] = totals_by_currency.get(currency, 0) + amount

    if totals_by_currency:
        value_chips = "".join(
            f'<span class="pipeline-value-chip">{cur}: {amt:,.0f}</span>'
            for cur, amt in totals_by_currency.items()
        )
        st.markdown(
            f'<div class="pipeline-value-row">{value_chips}</div>',
            unsafe_allow_html=True,
        )

    grouped = {stage: [] for stage in PIPELINE_STAGES}
    for lead in leads:
        stage = lead.get("status") or "New"
        grouped.setdefault(stage, []).append(lead)

    stage_cols = st.columns(len(grouped))
    for col, stage in zip(stage_cols, grouped.keys()):
        stage_leads = grouped[stage]
        with col:
            st.markdown(
                f'<div class="pipeline-col-header">{stage} '
                f'<span class="pipeline-col-count">{len(stage_leads)}</span></div>',
                unsafe_allow_html=True,
            )
            for lead in stage_leads:
                amount = _parse_amount(lead.get("budget_amount"))
                currency = lead.get("budget_currency") or ""
                amount_html = (
                    f'<div class="pipeline-card-amount">{currency} {amount:,.0f}</div>'
                    if amount is not None
                    else ""
                )
                st.markdown(
                    f"""
                    <div class="pipeline-card">
                        <div class="pipeline-card-name">{lead.get('company') or lead.get('name', 'Unnamed')}</div>
                        {amount_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def show(leads=None):
    st.markdown('<div class="eyebrow-label" style="margin-top:24px;">Performance Metrics</div>', unsafe_allow_html=True)
    render_summary_metrics()

    st.markdown('<div class="eyebrow-label" style="margin-top:24px;">Sales Pipeline (real leads only)</div>', unsafe_allow_html=True)
    render_pipeline_board(leads=leads)