import html
import json
import re

import streamlit as st
import streamlit.components.v1 as components
import requests
from database import get_all_leads, get_lead_details

API_BASE = "http://127.0.0.1:8000"

EMAIL_TYPE_OPTIONS = {
    "Cold email": "cold_email",
    "Follow-up email": "follow_up_email",
    "Re-engagement email": "re_engagement",
}

TONE_OPTIONS = ["Professional", "Warm", "Urgent"]
LENGTH_OPTIONS = ["Short", "Medium", "Long"]
GOAL_OPTIONS = ["Book a Demo", "Get a Reply", "Schedule a Call", "Share a Resource", "Request Feedback"]


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def _split_tags(text):
    """
    A lead's pain_points / business_goals are stored as one free-text
    field, but often contain several distinct items separated by a
    comma or pipe. Split those into individual tags, falling back to
    the whole string as a single item.
    """
    if not text:
        return []

    parts = re.split(r"[,|]", text)

    seen = set()
    tags = []

    for part in parts:
        cleaned = part.strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            tags.append(cleaned)

    return tags


def _initials(name):
    parts = [p for p in re.split(r"\s+", (name or "").strip()) if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


# ----------------------------------------------------------------------
# Backend calls
# ----------------------------------------------------------------------
def _generate_email(
    lead_id,
    pain_points_focus,
    business_goals_focus,
    email_type=None,
    tone=None,
    email_length=None,
    primary_goal=None,
    personalization_options=None,
):
    payload = {}

    if pain_points_focus:
        payload["pain_points_focus"] = pain_points_focus

    if business_goals_focus:
        payload["business_goals_focus"] = business_goals_focus

    if email_type:
        payload["email_type"] = email_type

    if tone:
        payload["tone"] = tone.lower()

    # Extra personalization inputs. These ride along as best-effort extra
    # fields — if the backend model doesn't know about them yet, FastAPI's
    # default pydantic behavior is to ignore unknown keys rather than fail
    # the request.
    if email_length:
        payload["email_length"] = email_length.lower()

    if primary_goal:
        payload["primary_goal"] = primary_goal

    if personalization_options:
        payload["personalization_options"] = personalization_options

    response = requests.post(
        f"{API_BASE}/email/generate/{lead_id}",
        json=payload or None,
        timeout=30,
    )
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise Exception(f"Email generation failed ({response.status_code}): {detail}")
    return response.json()


def _save_edits(campaign_id, subject, body):
    response = requests.put(
        f"{API_BASE}/email/edit/{campaign_id}",
        json={"email_subject": subject, "email_body": body},
        timeout=15,
    )
    if response.status_code != 200:
        raise Exception("Could not save your edits.")
    return response.json()


def _mark_sent(campaign_id):
    response = requests.put(f"{API_BASE}/email/send/{campaign_id}", timeout=15)
    if response.status_code != 200:
        raise Exception("Could not mark this email as sent.")
    return response.json()


def _focus_email_body_textarea():
    """
    When the person switches into edit mode, put the cursor into the
    Email Body textarea (at the end of the existing text) so they can
    start typing immediately instead of having to click into it first.
    """
    components.html(
        """
        <script>
        (function() {
          const doc = window.parent.document;
          const areas = doc.querySelectorAll('textarea[aria-label="Email Body"]');
          if (areas.length) {
            const ta = areas[areas.length - 1];
            ta.focus();
            const len = ta.value ? ta.value.length : 0;
            try { ta.setSelectionRange(len, len); } catch (e) {}
          }
        })();
        </script>
        """,
        height=0,
    )


def _render_copy_button(campaign_id, subject, body):
    """
    Renders a real, working 'Copy to Clipboard' button. Streamlit has no
    native clipboard widget, so this uses a small isolated HTML component
    with a JS clipboard call (with an execCommand fallback for older /
    embedded browser contexts) — clicking it copies the subject + body
    every time.
    """
    payload = json.dumps(f"Subject: {subject}\n\n{body}")
    uid = f"copy_{campaign_id}"

    components.html(
        f"""
        <div style="font-family:'Inter','Segoe UI',sans-serif;">
          <button id="{uid}_btn" onclick="{uid}_copy()" style="
                width:100%; box-sizing:border-box; padding:0.5rem 0.75rem;
                border-radius:8px; border:1px solid #e0c9ac; background:#ffffff;
                color:#8a4b1f; font-weight:600; font-size:14px; cursor:pointer;
                transition:all 0.12s ease;"
                onmouseover="this.style.background='#b5651d'; this.style.color='#fff'; this.style.borderColor='#b5651d';"
                onmouseout="this.style.background='#ffffff'; this.style.color='#8a4b1f'; this.style.borderColor='#e0c9ac';">
            &#128203; Copy to Clipboard
          </button>
          <div id="{uid}_msg" style="display:none; margin-top:4px; font-size:12.5px;
                color:#2f6f4f; text-align:center; font-weight:600;">Copied to clipboard!</div>
        </div>
        <script>
        function {uid}_copy() {{
          const text = {payload};
          function fallbackCopy(t) {{
            const ta = document.createElement('textarea');
            ta.value = t;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            try {{ document.execCommand('copy'); }} catch (e) {{}}
            document.body.removeChild(ta);
          }}
          if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
          }} else {{
            fallbackCopy(text);
          }}
          const msg = document.getElementById('{uid}_msg');
          msg.style.display = 'block';
          setTimeout(() => {{ msg.style.display = 'none'; }}, 1600);
        }}
        </script>
        """,
        height=62,
    )


# ----------------------------------------------------------------------
# Editable chip list (Key Pain Points / Business Goals)
# ----------------------------------------------------------------------
def _chip_list(namespace, lead_id, initial_tags):
    list_key = f"{namespace}_tags_{lead_id}"
    adding_key = f"{namespace}_adding_{lead_id}"
    version_key = f"{namespace}_add_version_{lead_id}"

    if list_key not in st.session_state:
        st.session_state[list_key] = list(initial_tags)
    if adding_key not in st.session_state:
        st.session_state[adding_key] = False
    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    tags = st.session_state[list_key]

    with st.container(key=f"{namespace}_chip_row_{lead_id}"):
        for i, tag in enumerate(list(tags)):
            if st.button(f"{tag}  ✕", key=f"{namespace}_chip_{lead_id}_{i}"):
                tags.pop(i)
                st.session_state[list_key] = tags
                st.rerun()
        if st.button("+ Add", key=f"{namespace}_add_toggle_{lead_id}"):
            st.session_state[adding_key] = not st.session_state[adding_key]
            st.rerun()

    if st.session_state[adding_key]:
        input_key = f"{namespace}_add_input_{lead_id}_{st.session_state[version_key]}"
        add_col, confirm_col = st.columns([3, 1])
        with add_col:
            new_val = st.text_input(
                "Add item", key=input_key, label_visibility="collapsed",
                placeholder=f"Type a new {'pain point' if namespace == 'pain' else 'goal'}...",
            )
        with confirm_col:
            if st.button("Add", key=f"{namespace}_confirm_{lead_id}", use_container_width=True):
                if new_val and new_val.strip():
                    tags.append(new_val.strip())
                    st.session_state[list_key] = tags
                st.session_state[adding_key] = False
                st.session_state[version_key] += 1
                st.rerun()

    return st.session_state[list_key]


# ----------------------------------------------------------------------
# "View Lead Details" modal
# ----------------------------------------------------------------------
@st.dialog("Lead Details")
def _lead_details_dialog(contact, company, industry, email, phone, details):
    st.markdown(
        f'<div class="oc-card-header" style="margin-bottom:14px;">'
        f'<span class="oc-card-icon">👤</span>'
        f'<span class="oc-card-title">{html.escape(contact or company or "Lead")}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    rows = [
        ("Company", company),
        ("Industry", industry),
        ("Email", email),
        ("Phone", phone),
        ("Location", details.get("location")),
        ("Company Size", details.get("company_size")),
        ("Job Title", details.get("job_title")),
        ("Lead Source", details.get("lead_source")),
        ("Purchase Timeline", details.get("purchase_timeline")),
        ("Current CRM", details.get("current_crm")),
        ("Status", details.get("status")),
        ("Pain Points", details.get("pain_points")),
        ("Business Goals", details.get("business_goals")),
        ("Notes", details.get("notes")),
    ]

    rows_html = "".join(
        f'<div class="info-row"><span class="info-key">{html.escape(k)}</span>'
        f'<span class="info-value">{html.escape(str(v)) if v not in (None, "") else "—"}</span></div>'
        for k, v in rows
    )
    st.markdown(rows_html, unsafe_allow_html=True)

    if st.button("Close", use_container_width=True, key="close_lead_details_dialog"):
        st.rerun()


# ----------------------------------------------------------------------
# Main render
# ----------------------------------------------------------------------
def show():
    leads = get_all_leads()
    if not leads:
        st.info("No leads available. Please add a lead first.")
        return

    lead_options = {f"{l[1]} ({l[3]})": l for l in leads}

    if "sl_expanded" not in st.session_state:
        st.session_state["sl_expanded"] = True
    if "pi_expanded" not in st.session_state:
        st.session_state["pi_expanded"] = True

    # ==================================================================
    # 1. Select Lead
    # ==================================================================
    with st.container(border=True, key="select_lead_card"):
        head_col, side_col = st.columns([0.86, 0.14])
        with head_col:
            st.markdown(
                '<div class="oc-step-head">'
                '<div class="oc-icon-box">👤</div>'
                '<div><div class="oc-step-title">Select Lead</div>'
                '<div class="oc-step-subtitle">Choose a lead to generate outreach.</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )
        with side_col:
            if st.button(
                "\u25be" if st.session_state["sl_expanded"] else "\u25b8",
                key="chevron_select_lead", help="Expand / collapse",
            ):
                st.session_state["sl_expanded"] = not st.session_state["sl_expanded"]
                st.rerun()

        selected = list(lead_options.keys())[0]
        lead_id = company = industry = contact = email = phone = None
        lead_details = {}

        if st.session_state["sl_expanded"]:
            row_col, btn_col = st.columns([0.74, 0.26], gap="medium")
            with row_col:
                avatar_col, select_col = st.columns([0.1, 0.9], gap="small")
                with select_col:
                    selected = st.selectbox(
                        "Select a lead", list(lead_options.keys()), label_visibility="collapsed"
                    )
                lead = lead_options[selected]
                lead_id, company, industry, contact, email, phone = (
                    lead[0], lead[1], lead[2], lead[3], lead[4], lead[5],
                )
                with avatar_col:
                    st.markdown(
                        f'<div class="oc-lead-avatar">{html.escape(_initials(contact or company))}</div>',
                        unsafe_allow_html=True,
                    )
            with btn_col:
                view_clicked = st.button(
                    "👁 View Lead Details", key="view_lead_details_btn", use_container_width=True
                )

            lead_details = get_lead_details(lead_id) or {}
            if view_clicked:
                _lead_details_dialog(contact, company, industry, email, phone, lead_details)
        else:
            lead = lead_options[selected]
            lead_id, company, industry, contact, email, phone = (
                lead[0], lead[1], lead[2], lead[3], lead[4], lead[5],
            )
            lead_details = get_lead_details(lead_id) or {}

    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

    # ==================================================================
    # 2. Personalization Inputs
    # ==================================================================
    with st.container(border=True, key="personalization_card"):
        head_col, side_col = st.columns([0.86, 0.14])
        with head_col:
            st.markdown(
                '<div class="oc-step-head">'
                '<div class="oc-icon-box">📝</div>'
                '<div><div class="oc-step-title">Personalization Inputs</div>'
                '<div class="oc-step-subtitle">Add details to personalize your email.</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )
        with side_col:
            if st.button(
                "\u25be" if st.session_state["pi_expanded"] else "\u25b8",
                key="chevron_personalization", help="Expand / collapse",
            ):
                st.session_state["pi_expanded"] = not st.session_state["pi_expanded"]
                st.rerun()

        tone = TONE_OPTIONS[0]
        length = LENGTH_OPTIONS[1]
        email_type_label = list(EMAIL_TYPE_OPTIONS.keys())[0]
        primary_goal = GOAL_OPTIONS[0]
        pain_tags = _split_tags(lead_details.get("pain_points"))
        goal_tags = _split_tags(lead_details.get("business_goals"))
        opt_recent_news = opt_benchmarks = opt_specific_pain = True
        opt_showcase_value = opt_social_proof = opt_personalize_sig = True

        if st.session_state["pi_expanded"]:
            st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

            row1_a, row1_b = st.columns(2, gap="large")
            with row1_a:
                st.markdown('<div class="pi-label">Tone of Email</div>', unsafe_allow_html=True)
                tone = st.selectbox("Tone of Email", TONE_OPTIONS, key=f"tone_{lead_id}", label_visibility="collapsed")
            with row1_b:
                st.markdown('<div class="pi-label">Email Length</div>', unsafe_allow_html=True)
                length = st.selectbox("Email Length", LENGTH_OPTIONS, index=1, key=f"length_{lead_id}", label_visibility="collapsed")

            row2_a, row2_b = st.columns(2, gap="large")
            with row2_a:
                st.markdown('<div class="pi-label">Email Type</div>', unsafe_allow_html=True)
                email_type_label = st.selectbox(
                    "Email Type", list(EMAIL_TYPE_OPTIONS.keys()), key=f"etype_{lead_id}", label_visibility="collapsed"
                )
            with row2_b:
                st.markdown('<div class="pi-label">Primary Goal</div>', unsafe_allow_html=True)
                primary_goal = st.selectbox("Primary Goal", GOAL_OPTIONS, key=f"goal_{lead_id}", label_visibility="collapsed")

            row3_a, row3_b = st.columns(2, gap="large")
            with row3_a:
                st.markdown('<div class="pi-label">Key Pain Points</div>', unsafe_allow_html=True)
                pain_tags = _chip_list("pain", lead_id, pain_tags)
            with row3_b:
                st.markdown('<div class="pi-label">Business Goals</div>', unsafe_allow_html=True)
                goal_tags = _chip_list("goal", lead_id, goal_tags)

            st.markdown('<hr class="oc-step-divider"/>', unsafe_allow_html=True)

            st.markdown('<div class="pi-label" style="margin-bottom:8px;">Personalization Options</div>', unsafe_allow_html=True)
            opt_col_a, opt_col_b = st.columns(2, gap="large")
            with opt_col_a:
                opt_recent_news = st.checkbox("Mention recent news / insights", value=True, key=f"opt_news_{lead_id}")
                opt_benchmarks = st.checkbox("Include industry benchmarks", value=True, key=f"opt_bench_{lead_id}")
                opt_specific_pain = st.checkbox("Include specific pain points", value=True, key=f"opt_pain_{lead_id}")
            with opt_col_b:
                opt_showcase_value = st.checkbox("Show case our value & differentiators", value=True, key=f"opt_value_{lead_id}")
                opt_social_proof = st.checkbox("Add social proof / credibility", value=True, key=f"opt_social_{lead_id}")
                opt_personalize_sig = st.checkbox("Personalize signature", value=True, key=f"opt_sig_{lead_id}")

    personalization_options = {
        "mention_recent_news": opt_recent_news,
        "include_industry_benchmarks": opt_benchmarks,
        "include_specific_pain_points": opt_specific_pain,
        "showcase_value_differentiators": opt_showcase_value,
        "add_social_proof_credibility": opt_social_proof,
        "personalize_signature": opt_personalize_sig,
    }

    def _run_generation():
        return _generate_email(
            lead_id,
            pain_tags,
            goal_tags,
            email_type=EMAIL_TYPE_OPTIONS[email_type_label],
            tone=tone,
            email_length=length,
            primary_goal=primary_goal,
            personalization_options=personalization_options,
        )

    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

    # ==================================================================
    # 3. Generate Mail
    # ==================================================================
    with st.container(border=True, key="generate_mail_card"):
        head_col, side_col = st.columns([0.62, 0.38])
        with head_col:
            st.markdown(
                '<div class="oc-step-head">'
                '<div class="oc-icon-box">✉️</div>'
                '<div><div class="oc-step-title">Generate Mail</div>'
                '<div class="oc-step-subtitle">Generate your personalized outreach email.</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )
        with side_col:
            st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
            generate_clicked = st.button(
                "✨  Generate Email", use_container_width=True, type="primary", key=f"generate_{lead_id}"
            )

    if generate_clicked:
        try:
            with st.spinner("AI is writing the email..."):
                campaign = _run_generation()
            st.session_state["latest_campaign"] = campaign
            st.session_state.pop(f"body_{campaign['id']}", None)
            st.session_state.pop(f"subject_{campaign['id']}", None)
            st.session_state.pop(f"editing_body_{campaign['id']}", None)
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the backend. Please make sure your "
                "FastAPI backend is running on http://127.0.0.1:8000."
            )
        except Exception as e:
            st.error(str(e))

    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

    # ==================================================================
    # AI Generated Email (full width, below the three steps)
    # ==================================================================
    with st.container(border=True, key="ai_email_card"):
        campaign = st.session_state.get("latest_campaign")
        has_campaign_for_lead = bool(campaign) and campaign.get("lead_id") == lead_id

        hcol1, hcol2 = st.columns([2.6, 1])
        with hcol1:
            st.markdown(
                '<div class="oc-card-header"><span class="oc-card-icon">✉️</span>'
                '<span class="oc-card-title">AI Generated Email</span></div>',
                unsafe_allow_html=True,
            )
        with hcol2:
            refresh_clicked = st.button(
                "↻ Refresh", key="refresh_email_btn", use_container_width=True,
                disabled=not has_campaign_for_lead,
            )

        if refresh_clicked and has_campaign_for_lead:
            try:
                with st.spinner("AI is regenerating the email..."):
                    campaign = _run_generation()
                st.session_state["latest_campaign"] = campaign
                cid = campaign["id"]
                st.session_state.pop(f"body_{cid}", None)
                st.session_state.pop(f"subject_{cid}", None)
                st.session_state.pop(f"editing_body_{cid}", None)
                st.rerun()
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the backend. Please make sure your "
                    "FastAPI backend is running on http://127.0.0.1:8000."
                )
            except Exception as e:
                st.error(str(e))

        campaign = st.session_state.get("latest_campaign")

        if not campaign or campaign.get("lead_id") != lead_id:
            st.markdown(
                '<div class="empty-email-state">Fill in the personalization inputs and click '
                '<b>Generate Email</b> to see your draft here.</div>',
                unsafe_allow_html=True,
            )
            st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
            return

        cid = campaign["id"]

        st.markdown(
            f'<div class="oc-to-row"><span>To</span>{html.escape(email or "No email on file")}</div>',
            unsafe_allow_html=True,
        )

        subject_key = f"subject_{cid}"
        if subject_key not in st.session_state:
            st.session_state[subject_key] = campaign.get("email_subject", "")

        st.markdown('<div class="oc-field-label-strong">Subject:</div>', unsafe_allow_html=True)
        subject = st.text_input("Subject", key=subject_key, label_visibility="collapsed")

        body_key = f"body_{cid}"
        if body_key not in st.session_state:
            st.session_state[body_key] = campaign.get("email_body", "")

        edit_key = f"editing_body_{cid}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = False

        is_editing = st.session_state[edit_key]

        # A single, persistent text_area is used for both the "display"
        # and "edit" states (toggling `disabled` rather than swapping to a
        # different widget/markdown). Switching from a plain markdown box
        # to a freshly-created text_area on click was what caused the
        # content to appear to vanish when entering edit mode; keeping the
        # same widget instance the whole time guarantees the text stays.
        body = st.text_area(
            "Email Body",
            key=body_key,
            height=260,
            label_visibility="collapsed",
            disabled=not is_editing,
        )
        if is_editing:
            _focus_email_body_textarea()

        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        copy_col, edit_col, send_col = st.columns(3)

        with copy_col:
            _render_copy_button(cid, subject, body)

        with edit_col:
            edit_label = "✓ Done Editing" if st.session_state[edit_key] else "✎ Edit Email"
            if st.button(edit_label, use_container_width=True, key=f"edit_toggle_{cid}"):
                st.session_state[edit_key] = not st.session_state[edit_key]
                st.rerun()

        with send_col:
            status = campaign.get("campaign_status", "Draft")
            if st.button(
                "📤 Send Email" if status != "Sent" else "✓ Sent",
                use_container_width=True,
                type="primary",
                key=f"send_{cid}",
                disabled=(status == "Sent"),
            ):
                try:
                    _save_edits(cid, subject, body)
                    updated = _mark_sent(cid)
                    st.session_state["latest_campaign"] = updated
                    st.success("Email saved and marked as sent.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
