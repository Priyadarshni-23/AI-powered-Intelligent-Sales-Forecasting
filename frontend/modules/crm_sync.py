import streamlit as st
import requests
from database import get_all_leads

API_BASE = "http://127.0.0.1:8000"

STATUS_BADGE = {
    "Success": "badge-cold",
    "Failed": "badge-hot",
    "Pending": "badge-warm",
}


def _sync_lead(lead_id):
    response = requests.post(f"{API_BASE}/crm/sync/{lead_id}", timeout=15)
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise Exception(f"CRM sync failed ({response.status_code}): {detail}")
    return response.json()


def _get_sync_logs(lead_id):
    response = requests.get(f"{API_BASE}/crm/{lead_id}", timeout=15)
    if response.status_code != 200:
        raise Exception("Could not load CRM sync history.")
    return response.json()


def show():
    st.markdown('<div class="card-title">CRM Sync Status</div>', unsafe_allow_html=True)
    st.markdown(
            '<p class="text-muted" style="font-size:12.5px; margin-top:-8px; margin-bottom:12px;">'
            "Displays the latest synchronization status for this lead with the connected CRM.</p>",
            unsafe_allow_html=True,
        )

    leads = get_all_leads()
    if not leads:
        st.info("No leads available. Please add a lead first.")
        return

    lead_options = {f"{l[1]} ({l[3]})": l for l in leads}
    selected = st.selectbox("Select a lead", list(lead_options.keys()), key="crm_lead_select")
    lead = lead_options[selected]
    lead_id = lead[0]

    if st.button("✨ Sync to CRM", use_container_width=True, key="crm_sync_btn", type="primary"):
        try:
            with st.spinner("Syncing lead to CRM..."):
                _sync_lead(lead_id)
            st.success("Lead synced.")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the backend. Please make sure your "
                "FastAPI backend is running on http://127.0.0.1:8000."
            )
        except Exception as e:
            st.error(str(e))

    st.divider()
    st.markdown('<div class="eyebrow-label">Sync History</div>', unsafe_allow_html=True)

    try:
        logs = _get_sync_logs(lead_id)
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the backend. Please make sure your "
            "FastAPI backend is running on http://127.0.0.1:8000."
        )
        return
    except Exception as e:
        st.error(str(e))
        return

    if not logs:
        st.markdown(
            '<p class="text-muted" style="font-size:14px;">'
            "This lead hasn't been synced yet.</p>",
            unsafe_allow_html=True,
        )
        return

    logs_sorted = sorted(logs, key=lambda l: l.get("synced_at") or "", reverse=True)

    items_html = ""
    for log in logs_sorted:
        badge_class = STATUS_BADGE.get(log.get("sync_status"), "badge-new")
        synced_at = (log.get("synced_at") or "")[:16].replace("T", " ")
        error = log.get("error_message") or "No errors"

        # NOTE: no leading whitespace on any line here. Markdown treats
        # lines indented by 4+ spaces as a preformatted code block, which
        # is why the HTML was showing up as literal text instead of being
        # rendered — unsafe_allow_html=True doesn't help once Markdown has
        # already decided it's a code block.
        items_html += (
            '<div class="crm-log-item">'
            '<div class="crm-log-top">'
            f'<span class="crm-log-name">{log.get("crm_name", "CRM")} · {log.get("sync_type", "Sync")}</span>'
            f'<span class="badge {badge_class}">{log.get("sync_status", "Unknown")}</span>'
            '</div>'
            f'<div class="crm-log-meta">{log.get("records_synced", 0)} record(s) synced · {synced_at}</div>'
            f'<div class="crm-log-meta">Error: {error}</div>'
            '</div>'
        )

    st.markdown(items_html, unsafe_allow_html=True)