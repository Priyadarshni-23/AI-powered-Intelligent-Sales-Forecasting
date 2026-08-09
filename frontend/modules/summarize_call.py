import streamlit as st
import requests
from database import get_all_leads

API_BASE = "http://127.0.0.1:8000"


def _generate_summary(lead_id):
    response = requests.post(f"{API_BASE}/summary/generate/{lead_id}", timeout=30)
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise Exception(f"Summary generation failed ({response.status_code}): {detail}")
    return response.json()


def _get_summaries(lead_id):
    response = requests.get(f"{API_BASE}/summary/{lead_id}", timeout=15)
    if response.status_code != 200:
        raise Exception("Could not load meeting summaries.")
    return response.json()


def _split_lines(text):
    if not text:
        return []
    parts = [p.strip(" -\u2022\t") for p in text.replace("\r", "").split("\n")]
    return [p for p in parts if p]


def show():
    st.markdown('<div class="card-title">Meeting Summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="text-muted" style="font-size:12.5px; margin-top:-8px; margin-bottom:12px;">'
        "Generated from this lead's stored notes, not a pasted transcript.</p>",
        unsafe_allow_html=True,
    )

    leads = get_all_leads()
    if not leads:
        st.info("No leads available. Please add a lead first.")
        return

    lead_options = {f"{l[1]} ({l[3]})": l for l in leads}
    selected = st.selectbox("Select a lead", list(lead_options.keys()), key="summary_lead_select")
    lead = lead_options[selected]
    lead_id = lead[0]

    if st.button("✨ Generate Meeting Summary", use_container_width=True, key="gen_summary_btn", type="primary"):
        try:
            with st.spinner("AI is summarizing..."):
                _generate_summary(lead_id)
            st.success("Summary generated.")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the backend. Please make sure your "
                "FastAPI backend is running on http://127.0.0.1:8000."
            )
        except Exception as e:
            st.error(str(e))

    st.divider()

    try:
        summaries = _get_summaries(lead_id)
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the backend. Please make sure your "
            "FastAPI backend is running on http://127.0.0.1:8000."
        )
        return
    except Exception as e:
        st.error(str(e))
        return

    if not summaries:
        st.markdown(
            '<p class="text-muted" style="font-size:14px;">'
            "No summaries generated yet for this lead.</p>",
            unsafe_allow_html=True,
        )
        return

    summaries_sorted = sorted(summaries, key=lambda s: s.get("meeting_date") or "", reverse=True)
    latest = summaries_sorted[0]

    meeting_date = (latest.get("meeting_date") or "")[:16].replace("T", " ")
    st.markdown(
        f"""
        <div class="info-row"><span class="info-key">Meeting</span><span class="info-value">{latest.get('meeting_title', '')}</span></div>
        <div class="info-row"><span class="info-key">Type</span><span class="info-value">{latest.get('interaction_type', '')}</span></div>
        <div class="info-row"><span class="info-key">Date</span><span class="info-value">{meeting_date}</span></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="eyebrow-label" style="margin-top:16px;">Key Discussion Points</div>', unsafe_allow_html=True)
    points = _split_lines(latest.get("ai_summary", "")) or _split_lines(latest.get("interaction_notes", ""))
    if points:
        points_html = "".join(f"<li>{p}</li>" for p in points)
        st.markdown(f'<ul class="insight-list">{points_html}</ul>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="text-muted" style="font-size:14px;">No summary text returned.</p>', unsafe_allow_html=True)

    st.markdown('<div class="eyebrow-label" style="margin-top:16px;">Action Items</div>', unsafe_allow_html=True)
    actions = _split_lines(latest.get("action_items", ""))
    if actions:
        items_html = "".join(f'<div class="action-item">\u2610 {a}</div>' for a in actions)
        st.markdown(items_html, unsafe_allow_html=True)
    else:
        st.markdown('<p class="text-muted" style="font-size:14px;">No action items detected.</p>', unsafe_allow_html=True)

    if len(summaries_sorted) > 1:
        remaining = len(summaries_sorted) - 1
        with st.expander(f"View {remaining} earlier summar{'y' if remaining == 1 else 'ies'}"):
            for s in summaries_sorted[1:]:
                d = (s.get("meeting_date") or "")[:16].replace("T", " ")
                st.markdown(f"**{s.get('meeting_title', '')}** \u2014 {d}")
                st.write(s.get("ai_summary", ""))
                st.markdown("---")