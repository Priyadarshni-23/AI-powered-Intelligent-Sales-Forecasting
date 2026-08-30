import csv
import io
import textwrap

import streamlit as st
from database import (
    get_all_leads,
    get_all_leads_full,
    get_lead_by_id,
    get_lead_details,
    update_lead,
    update_lead_status,
    delete_lead,
    add_lead,
    find_duplicate_lead,
)

STATUS_OPTIONS = ["New", "Hot", "Warm", "Cold", "Contacted", "Qualified"]

BADGE_MAP = {
    "Hot": "badge-hot",
    "Warm": "badge-warm",
    "New": "badge-new",
    "Cold": "badge-cold",
}

# ============================================================
# Dropdown Options
# ============================================================

INDUSTRY_OPTIONS = [
    "Technology",
    "Software",
    "IT Services",
    "Finance",
    "Healthcare",
    "Manufacturing",
    "Retail",
    "Education",
    "Real Estate",
    "Automotive",
    "Other",
]

LOCATION_OPTIONS = [
    "India",
    "USA",
    "UK",
    "Germany",
    "Australia",
    "Other",
]

COMPANY_SIZE_OPTIONS = [
    "Startup",
    "Small",
    "Medium",
    "Enterprise",
    "Other",
]

JOB_TITLE_OPTIONS = [
    "CEO",
    "CTO",
    "Sales Manager",
    "Marketing Head",
    "Other",
]

LEAD_SOURCE_OPTIONS = [
    "LinkedIn",
    "Website",
    "Referral",
    "Cold Call",
    "Conference",
    "Other",
]

PURCHASE_TIMELINE_OPTIONS = [
    "Immediate",
    "1 Month",
    "3 Months",
    "6+ Months",
    "Other",
]

CRM_OPTIONS = [
    "Salesforce",
    "HubSpot",
    "Zoho CRM",
    "Excel",
    "No CRM",
    "Other",
]

PAIN_POINT_OPTIONS = [
    "Low Lead Conversion",
    "Poor Follow-up",
    "Manual Process",
    "No CRM",
    "Other",
]

BUSINESS_GOAL_OPTIONS = [
    "Increase Sales",
    "Improve Customer Retention",
    "Automate Sales",
    "Better Analytics",
    "Other",
]

BUDGET_CURRENCY_OPTIONS = [
    "Dollars ($)",
    "Rupees (₹)",
    "Other",
]


def _badge_class(status):
    return BADGE_MAP.get(status, "badge-new")


def _html(raw):
    """
    Strip common leading whitespace from a multi-line HTML string.

    Without this, HTML built from an f-string inside deeply-nested
    `with` blocks keeps the Python source's indentation as part of
    the string. Markdown treats 4+ leading spaces as an "indented
    code block", so the tags get printed as literal text instead of
    being rendered as HTML. Dedent + strip fixes that.
    """
    return textwrap.dedent(raw).strip()


# ============================================================
# Dropdown Helper
# ============================================================

def _dropdown_with_other(
    label,
    options,
    default_value="",
    key=None,
):
    """
    Displays a dropdown, with its "Other" text input placed in a
    column right next to it (same row) rather than stacked below it.

    Stacking the "Enter X" box below the dropdown was what caused the
    misalignment: it silently added an extra row's worth of height to
    whichever macro-column happened to have "Other" selected, so that
    column's fields drifted out of sync with the neighboring column.
    Keeping the dropdown and its text box in the same row means every
    field takes up the same vertical space whether "Other" is picked
    or not, so both columns stay lined up.
    """

    current_value = default_value or ""

    if current_value in options and current_value != "Other":
        selected_index = options.index(current_value)
    else:
        selected_index = options.index("Other") if "Other" in options else 0

    dropdown_col, other_col = st.columns(2)

    with dropdown_col:
        selected = st.selectbox(
            label,
            options,
            index=selected_index,
            key=key,
        )

    with other_col:
        if selected == "Other":
            other_value = st.text_input(
                f"Enter {label.lower()}",
                value="" if current_value in options else current_value,
                key=f"{key}_other" if key else f"{label}_other",
            )

            return other_value.strip()

        # Keep an empty placeholder here (same label height as a real
        # widget) so the row height matches fields where "Other" IS
        # selected, keeping every row the same height either way.
        st.markdown(
            "<div style='height:2.6rem;'>&nbsp;</div>",
            unsafe_allow_html=True,
        )

    return selected


# ============================================================
# Add Lead Form
# ============================================================

def _render_add_lead_form():

    with st.form("add_lead_form", clear_on_submit=True):

        st.markdown("#### Basic lead information")

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Company name")
            contact_name = st.text_input("Contact name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")

        with col2:
            location = st.text_input("Location")
            industry = st.text_input("Industry")
            company_size = st.text_input("Company size")
            job_title = st.text_input("Job title")

        st.markdown("#### Budget information")

        budget_col1, budget_col2 = st.columns(2)

        with budget_col1:
            budget_currency = st.text_input(
                "Budget currency",
                placeholder="Example: Dollars ($), Rupees (₹)"
            )

        with budget_col2:
            budget_amount = st.text_input(
                "Budget amount",
                placeholder="Example: 50000"
            )

        st.markdown("#### Sales information")

        sales_col1, sales_col2 = st.columns(2)

        with sales_col1:
            lead_source = st.text_input(
                "Lead source",
                placeholder="Example: LinkedIn, Website, Referral"
            )

            purchase_timeline = st.text_input(
                "Purchase timeline",
                placeholder="Example: Immediate, 3 Months, 6+ Months"
            )

            current_crm = st.text_input(
                "Current CRM",
                placeholder="Example: Salesforce, HubSpot, Zoho CRM"
            )

        with sales_col2:
            pain_points = st.text_input(
                "Pain points",
                placeholder="Example: Low lead conversion, Manual follow-up"
            )

            business_goals = st.text_input(
                "Business goals",
                placeholder="Example: Increase sales, Automate sales"
            )

            status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                key="add_status",
            )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Add lead",
            use_container_width=True,
        )

        if submitted:

            fields = {
                "Company name": company_name,
                "Industry": industry,
                "Contact name": contact_name,
                "Email": email,
                "Phone": phone,
            }

            missing = [
                name
                for name, val in fields.items()
                if not val or not val.strip()
            ]

            if missing:
                st.error(
                    f"All basic fields are required. "
                    f"Missing: {', '.join(missing)}"
                )

            else:

                duplicate = find_duplicate_lead(
                    email.strip(),
                    phone.strip(),
                )

                if duplicate:

                    st.warning(
                        "A lead with this email or phone already exists: "
                        f"{duplicate[1]}"
                    )

                else:

                    result = add_lead(
                        company_name=company_name.strip(),
                        industry=industry.strip(),
                        contact_name=contact_name.strip(),
                        email=email.strip(),
                        phone=phone.strip(),
                        location=location.strip(),
                        company_size=company_size.strip(),
                        job_title=job_title.strip(),
                        budget_currency=budget_currency.strip(),
                        budget_amount=budget_amount.strip(),
                        lead_source=lead_source.strip(),
                        purchase_timeline=purchase_timeline.strip(),
                        current_crm=current_crm.strip(),
                        pain_points=pain_points.strip(),
                        business_goals=business_goals.strip(),
                        status=status,
                        notes=notes.strip(),
                    )

                    st.session_state.selected_lead_id = result.get(
                        "id",
                        result.get("lead_id"),
                    )

                    st.success("Lead added successfully.")

                    st.rerun()
# ============================================================
# Search List
# ============================================================

def _render_search_list(leads):

    with st.container(height=520, border=True):

        search = st.text_input(
            "Search leads",
            placeholder="Search by company or contact name",
            label_visibility="collapsed",
        )

        filtered = leads

        if search:

            q = search.lower().strip()

            filtered = [
                l
                for l in leads
                if q in l[1].lower()
                or q in l[3].lower()
            ]

        total_matches = len(filtered)

        filtered = filtered[:20]

        count_label = (
            f"{total_matches} lead"
            f"{'s' if total_matches != 1 else ''}"
        )

        if total_matches > 20:

            count_label += (
                " (showing first 20 — refine your search)"
            )

        st.markdown(
            _html(
                f"""
                <p style='font-size:12.5px;
                color:var(--text-secondary, #8a7563);
                margin:6px 0 10px;'>
                {count_label}
                </p>
                """
            ),
            unsafe_allow_html=True,
        )

        if not filtered:

            st.info(
                "No leads match your search."
            )

            return

        for lead in filtered:

            (
                lead_id,
                company,
                industry,
                contact,
                email,
                phone,
                status,
                created_at,
            ) = lead

            is_selected = (
                st.session_state.get(
                    "selected_lead_id"
                ) == lead_id
            )

            badge_class = _badge_class(
                status or "New"
            )

            with st.container(border=True):

                info_col, btn_col = st.columns(
                    [3, 1],
                    vertical_alignment="center",
                )

                with info_col:

                    active_class = (
                        "lead-list-item-active"
                        if is_selected
                        else ""
                    )

                    st.markdown(
                        _html(
                            f"""
                            <div class="lead-list-item {active_class}">
                                <div class="lead-company">
                                    {company}
                                    <span class="badge {badge_class}">
                                        {status or 'New'}
                                    </span>
                                </div>
                                <div class="lead-meta">
                                    {contact}
                                    &nbsp;|&nbsp;
                                    {industry}
                                </div>
                            </div>
                            """
                        ),
                        unsafe_allow_html=True,
                    )

                with btn_col:

                    if st.button(
                        "Viewing"
                        if is_selected
                        else "View",
                        key=f"select_{lead_id}",
                        use_container_width=True,
                        disabled=is_selected,
                    ):

                        st.session_state.selected_lead_id = lead_id

                        st.rerun()


# ============================================================
# Detail Panel
# ============================================================

def _render_detail_panel():

    lead_id = st.session_state.get(
        "selected_lead_id"
    )

    if lead_id is None:

        st.markdown(
            _html(
                """
                <div class="lead-empty-state">
                    <div class="lead-empty-icon">
                        <svg width="42" height="42" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect x="6" y="6" width="27" height="34" rx="4" fill="var(--brown-50)" stroke="var(--brown-300)" stroke-width="2"/>
                            <circle cx="14.5" cy="16" r="4" fill="var(--brown-300)"/>
                            <rect x="9.5" y="24" width="19" height="2.5" rx="1.25" fill="var(--brown-300)"/>
                            <rect x="9.5" y="29.5" width="13" height="2.5" rx="1.25" fill="var(--brown-300)"/>
                            <circle cx="32.5" cy="32.5" r="8" fill="#ffffff" stroke="var(--gold-600)" stroke-width="2.5"/>
                            <line x1="38" y1="38" x2="43.5" y2="43.5" stroke="var(--gold-600)" stroke-width="2.5" stroke-linecap="round"/>
                        </svg>
                    </div>
                    <p>
                        Select a lead from the list to view details
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        return

    # --------------------------------------------------------
    # Real Lead
    # --------------------------------------------------------

    lead = get_lead_by_id(
        lead_id
    )

    if lead is None:

        st.session_state.selected_lead_id = None

        st.info(
            "That lead no longer exists."
        )

        return

    # Get full lead details from backend
    full_lead = get_lead_details(
        lead_id
    )

    if full_lead is None:

        st.session_state.selected_lead_id = None

        st.info(
            "That lead no longer exists."
        )

        return

    # --------------------------------------------------------
    # Existing Lead Data
    # --------------------------------------------------------

    company = full_lead.get(
        "company",
        "",
    )

    contact = full_lead.get(
        "name",
        "",
    )

    email = full_lead.get(
        "email",
        "",
    )

    phone = full_lead.get(
        "phone",
        "",
    )

    industry = full_lead.get(
        "industry",
        "",
    )

    location = full_lead.get(
        "location",
        "",
    )

    company_size = full_lead.get(
        "company_size",
        "",
    )

    job_title = full_lead.get(
        "job_title",
        "",
    )

    budget_currency = full_lead.get(
        "budget_currency",
        "",
    )

    budget_amount = full_lead.get(
        "budget_amount",
        "",
    )

    lead_source = full_lead.get(
        "lead_source",
        "",
    )

    purchase_timeline = full_lead.get(
        "purchase_timeline",
        "",
    )

    current_crm = full_lead.get(
        "current_crm",
        "",
    )

    pain_points = full_lead.get(
        "pain_points",
        "",
    )

    business_goals = full_lead.get(
        "business_goals",
        "",
    )

    status = full_lead.get(
        "status",
        "New",
    )

    notes = full_lead.get(
        "notes",
        "",
    )

    # --------------------------------------------------------
    # Detail Header
    # --------------------------------------------------------

    st.markdown(
        _html(
            f"""
            <div class="detail-header">
                <h3>{company}</h3>
                <span class="badge {_badge_class(status or 'New')}">
                    {status or 'New'}
                </span>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Edit Lead Form
    # --------------------------------------------------------

    with st.form(
        f"edit_lead_{lead_id}"
    ):

        # ====================================================
        # Basic Lead Information
        # ====================================================

        st.markdown(
            "#### Basic lead information"
        )

        col1, col2 = st.columns(2)

        with col1:

            new_company = st.text_input(
                "Company name",
                value=company or "",
            )

            new_contact = st.text_input(
                "Contact name",
                value=contact or "",
            )

            new_email = st.text_input(
                "Email",
                value=email or "",
            )

            new_phone = st.text_input(
                "Phone",
                value=phone or "",
            )

        with col2:

            # Manual text input instead of dropdown
            new_location = st.text_input(
                "Location",
                value=location or "",
                placeholder="Example: Hyderabad, India",
            )

            # Manual text input instead of dropdown
            new_industry = st.text_input(
                "Industry",
                value=industry or "",
                placeholder="Example: Technology",
            )

            # Manual text input instead of dropdown
            new_company_size = st.text_input(
                "Company size",
                value=company_size or "",
                placeholder="Example: Enterprise",
            )

            # Manual text input instead of dropdown
            new_job_title = st.text_input(
                "Job title",
                value=job_title or "",
                placeholder="Example: CEO",
            )

        # ====================================================
        # Budget Information
        # ====================================================

        st.markdown(
            "#### Budget information"
        )

        budget_col1, budget_col2 = st.columns(2)

        with budget_col1:

            # Manual text input instead of dropdown
            new_budget_currency = st.text_input(
                "Budget currency",
                value=budget_currency or "",
                placeholder="Example: Dollars ($) or Rupees (₹)",
            )

        with budget_col2:

            new_budget_amount = st.text_input(
                "Budget amount",
                value=budget_amount or "",
                placeholder="Example: 50000",
            )

        # ====================================================
        # Sales Information
        # ====================================================

        st.markdown(
            "#### Sales information"
        )

        sales_col1, sales_col2 = st.columns(2)

        with sales_col1:

            # Manual text input instead of dropdown
            new_lead_source = st.text_input(
                "Lead source",
                value=lead_source or "",
                placeholder="Example: LinkedIn",
            )

            # Manual text input instead of dropdown
            new_purchase_timeline = st.text_input(
                "Purchase timeline",
                value=purchase_timeline or "",
                placeholder="Example: 3 Months",
            )

            # Manual text input instead of dropdown
            new_current_crm = st.text_input(
                "Current CRM",
                value=current_crm or "",
                placeholder="Example: Salesforce",
            )

        with sales_col2:

            # Manual text input instead of dropdown
            new_pain_points = st.text_input(
                "Pain points",
                value=pain_points or "",
                placeholder="Example: Manual follow-up, Low conversion",
            )

            # Manual text input instead of dropdown
            new_business_goals = st.text_input(
                "Business goals",
                value=business_goals or "",
                placeholder="Example: Increase sales, Automate process",
            )

            # Status dropdown is kept unchanged
            new_status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=(
                    STATUS_OPTIONS.index(status)
                    if status in STATUS_OPTIONS
                    else 0
                ),
            )

        # ====================================================
        # Notes
        # ====================================================

        new_notes = st.text_area(
            "Notes",
            value=notes or "",
            placeholder="Add any additional information about this lead...",
        )

        # ====================================================
        # Save / Delete Buttons
        # ====================================================

        save_col, delete_col = st.columns(
            [3, 1]
        )

        with save_col:

            save_clicked = st.form_submit_button(
                "Save changes",
                use_container_width=True,
            )

        with delete_col:

            delete_clicked = st.form_submit_button(
                "Delete",
                use_container_width=True,
            )

        # ====================================================
        # Save Changes
        # ====================================================

        if save_clicked:

            update_lead(
                lead_id=lead_id,
                company_name=new_company.strip(),
                industry=new_industry.strip(),
                contact_name=new_contact.strip(),
                email=new_email.strip(),
                phone=new_phone.strip(),
                location=new_location.strip(),
                company_size=new_company_size.strip(),
                job_title=new_job_title.strip(),
                budget_currency=new_budget_currency.strip(),
                budget_amount=new_budget_amount.strip(),
                lead_source=new_lead_source.strip(),
                purchase_timeline=new_purchase_timeline.strip(),
                current_crm=new_current_crm.strip(),
                pain_points=new_pain_points.strip(),
                business_goals=new_business_goals.strip(),
                status=new_status,
                notes=new_notes.strip(),
            )

            st.success(
                "Lead updated."
            )

            st.rerun()

        # ====================================================
        # Delete Clicked
        # ====================================================

        if delete_clicked:

            st.session_state.confirm_delete_id = lead_id

            st.rerun()

    # --------------------------------------------------------
    # Delete Confirmation
    # --------------------------------------------------------

    if (
        st.session_state.get(
            "confirm_delete_id"
        )
        == lead_id
    ):

        st.markdown(
            _html(
                f"""
                <div class="duplicate-alert">
                    <h4>Confirm deletion</h4>
                    <p>
                        Delete <b>{company}</b> permanently?
                        This can't be undone.
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        yes_col, no_col = st.columns(2)

        with yes_col:

            if st.button(
                "Yes, delete",
                key=f"confirm_yes_{lead_id}",
                use_container_width=True,
            ):

                delete_lead(
                    lead_id
                )

                st.session_state.selected_lead_id = None

                st.session_state.confirm_delete_id = None

                st.success(
                    f"'{company}' deleted."
                )

                st.rerun()

        with no_col:

            if st.button(
                "Cancel",
                key=f"confirm_no_{lead_id}",
                use_container_width=True,
            ):

                st.session_state.confirm_delete_id = None

                st.rerun()

# ============================================================
# Main Leads Page
# ============================================================

# ============================================================
# CSV Import
# ============================================================

def _render_import_results(summary):

    st.markdown(
        '<div class="import-complete-banner">Import complete.</div>',
        unsafe_allow_html=True,
    )

    stats = [
        ("Total Rows", summary["total_rows"], "c1"),
        ("Created", summary["added_count"], "c4"),
        ("Duplicates Skipped", summary["skipped_count"], "c3"),
        ("Errors", summary["failed_count"], "c2"),
    ]

    cols = st.columns(len(stats))

    for col, (label, value, color_class) in zip(cols, stats):
        with col:
            st.markdown(
                _html(
                    f"""
                    <div class="stat-card {color_class}">
                        <div class="stat-label">{label}</div>
                        <div class="stat-value">{value}</div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    results = summary["results"]

    if not results:
        return

    status_badge_map = {
        "Created": "badge-cold",
        "Duplicate": "badge-warm",
        "Failed": "badge-hot",
    }

    rows_html = []

    for r in results:
        badge_class = status_badge_map.get(r["status"], "badge-new")
        rows_html.append(
            _html(
                f"""
                <tr>
                    <td>{r['row']}</td>
                    <td><span class="badge {badge_class}">{r['status']}</span></td>
                    <td>{r['company'] or '&mdash;'}</td>
                    <td class="import-detail-cell">{r['detail'] or '&mdash;'}</td>
                </tr>
                """
            )
        )

    table_html = _html(
        f"""
        <div class="import-results-wrap">
            <table class="import-results-table">
                <thead>
                    <tr>
                        <th>Row</th>
                        <th>Status</th>
                        <th>Company</th>
                        <th>Detail</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
        """
    )

    st.markdown(table_html, unsafe_allow_html=True)


def _render_csv_upload():
    st.markdown("#### Import leads from CSV")

    st.caption(
        "Upload a CSV file containing your lead information. "
        "Duplicate leads based on email or phone will be skipped."
    )

    if "csv_import_summary" not in st.session_state:
        st.session_state.csv_import_summary = None

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"],
        key="lead_csv_uploader",
    )

    if uploaded_file is not None:

        try:
            raw_bytes = uploaded_file.getvalue()

            try:
                text = raw_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw_bytes.decode("latin-1")

            reader = csv.DictReader(io.StringIO(text))

            rows = list(reader)

            if not rows:
                st.warning("The uploaded CSV file is empty.")
                return

            # Normalize header names (case/whitespace-insensitive)
            fieldnames = reader.fieldnames or []
            normalized_map = {name: (name or "").strip().lower() for name in fieldnames}

            # Required fields
            required_columns = [
                "name",
                "company",
                "email",
                "phone",
                "industry",
            ]

            present_columns = set(normalized_map.values())

            missing_columns = [
                col for col in required_columns
                if col not in present_columns
            ]

            if missing_columns:
                st.error(
                    "Missing required CSV columns: "
                    + ", ".join(missing_columns)
                )
                return

            st.write(
                f"Found **{len(rows)} lead(s)** in the CSV file."
            )

            if st.button(
                "Import CSV Leads",
                use_container_width=True,
                key="import_csv_leads",
            ):

                added_count = 0
                skipped_count = 0
                failed_count = 0
                results = []

                progress = st.progress(0)

                def get_value(row, column):
                    for original_name, normalized_name in normalized_map.items():
                        if normalized_name == column:
                            value = row.get(original_name, "")
                            return "" if value is None else str(value).strip()
                    return ""

                total_rows = len(rows)

                for index, row in enumerate(rows):

                    csv_row_number = index + 2
                    company = get_value(row, "company")

                    try:
                        name = get_value(row, "name")
                        email = get_value(row, "email")
                        phone = get_value(row, "phone")
                        industry = get_value(row, "industry")

                        # Check required values
                        if not all([
                            name,
                            company,
                            email,
                            phone,
                            industry,
                        ]):
                            failed_count += 1
                            results.append({
                                "row": csv_row_number,
                                "status": "Failed",
                                "company": company,
                                "detail": "Missing one or more required fields.",
                            })
                            continue

                        # Duplicate check
                        duplicate = find_duplicate_lead(
                            email,
                            phone,
                        )

                        if duplicate:
                            skipped_count += 1
                            results.append({
                                "row": csv_row_number,
                                "status": "Duplicate",
                                "company": company,
                                "detail": "A matching lead already exists.",
                            })
                            continue

                        # Add lead to backend
                        add_lead(
                            company_name=company,
                            industry=industry,
                            contact_name=name,
                            email=email,
                            phone=phone,
                            location=get_value(row, "location"),
                            company_size=get_value(row, "company_size"),
                            job_title=get_value(row, "job_title"),
                            budget_currency=get_value(row, "budget_currency"),
                            budget_amount=get_value(row, "budget_amount"),
                            lead_source=get_value(row, "lead_source"),
                            purchase_timeline=get_value(
                                row, "purchase_timeline"
                            ),
                            current_crm=get_value(row, "current_crm"),
                            pain_points=get_value(row, "pain_points"),
                            business_goals=get_value(
                                row, "business_goals"
                            ),
                            status=get_value(row, "status") or "New",
                            notes=get_value(row, "notes"),
                        )

                        added_count += 1
                        results.append({
                            "row": csv_row_number,
                            "status": "Created",
                            "company": company,
                            "detail": "",
                        })

                    except Exception as e:
                        failed_count += 1
                        results.append({
                            "row": csv_row_number,
                            "status": "Failed",
                            "company": company,
                            "detail": str(e),
                        })

                    progress.progress(
                        (index + 1) / total_rows
                    )

                st.session_state.csv_import_summary = {
                    "total_rows": total_rows,
                    "added_count": added_count,
                    "skipped_count": skipped_count,
                    "failed_count": failed_count,
                    "results": results,
                }

                st.rerun()

        except Exception as e:
            st.error(
                f"Could not read the CSV file: {e}"
            )

    summary = st.session_state.csv_import_summary

    if summary:
        st.markdown(
            "<div style='margin-top:14px;'></div>",
            unsafe_allow_html=True,
        )
        _render_import_results(summary)

        if summary["added_count"] > 0:
            st.info(
                "Refresh the Leads list to see the imported leads."
            )

# ============================================================
# Leads Directory Table
# ============================================================

def _full_lead_id(full_lead):
    return full_lead.get("id", full_lead.get("lead_id"))


def _render_leads_directory_table(leads):

    st.markdown(
        '<div class="section-title" style="margin-bottom:4px; font-size:20px;">Lead Records Directory</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="section-subtitle">A complete record of every lead in the system, with full profile details.</p>',
        unsafe_allow_html=True,
    )

    try:
        full_leads = get_all_leads_full()
    except Exception:
        full_leads = []

    full_by_id = {
        _full_lead_id(full_lead): full_lead
        for full_lead in full_leads
    }

    if not leads:
        st.info("No leads to show yet.")
        return

    rows_html = []

    for lead in leads:

        (
            lead_id,
            company,
            industry,
            contact,
            email,
            phone,
            status,
            created_at,
        ) = lead

        extra = full_by_id.get(lead_id, {})

        location = extra.get("location") or "—"
        company_size = extra.get("company_size") or "—"
        lead_source = extra.get("lead_source") or "—"

        budget_currency = extra.get("budget_currency") or ""
        budget_amount = extra.get("budget_amount") or ""
        budget = f"{budget_currency} {budget_amount}".strip() or "—"

        badge_class = _badge_class(status or "New")

        rows_html.append(
            _html(
                f"""
                <tr>
                    <td class="leads-dir-id">{lead_id}</td>
                    <td>{company or '&mdash;'}</td>
                    <td>{contact or '&mdash;'}</td>
                    <td>{email or '&mdash;'}</td>
                    <td>{phone or '&mdash;'}</td>
                    <td>{industry or '&mdash;'}</td>
                    <td>{location}</td>
                    <td>{company_size}</td>
                    <td>{lead_source}</td>
                    <td>{budget}</td>
                    <td><span class="badge {badge_class}">{status or 'New'}</span></td>
                </tr>
                """
            )
        )

    table_html = _html(
        f"""
        <div class="leads-directory-wrap">
            <table class="leads-directory-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Company</th>
                        <th>Contact</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Industry</th>
                        <th>Location</th>
                        <th>Company size</th>
                        <th>Lead source</th>
                        <th>Budget</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
        """
    )

    st.markdown(table_html, unsafe_allow_html=True)


def show():

    if "selected_lead_id" not in st.session_state:

        st.session_state.selected_lead_id = None

    st.markdown('<div class="section-title" style="margin-bottom:0;">Leads</div>', unsafe_allow_html=True)

    leads = get_all_leads()

    list_col, detail_col = st.columns(
        [1.2, 1.3]
    )

    with list_col:

        _render_search_list(
            leads
        )

    with detail_col:

        with st.container(
            height=520,
            border=True,
        ):

            _render_detail_panel()

    st.markdown(
        "<div style='margin-top:28px;'></div>",
        unsafe_allow_html=True,
    )

    _render_leads_directory_table(leads)