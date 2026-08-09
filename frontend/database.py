import requests

API_BASE = "http://127.0.0.1:8000"


def _raise_with_detail(response):
    """
    Raise an HTTPError with the backend's actual error detail included.

    Plain `response.raise_for_status()` only produces a generic message
    like "400 Client Error: Bad Request for url: ...", which hides the
    real reason (e.g. a FastAPI validation error). This pulls the
    `detail` (or full body) out of the response and puts it in the
    exception message so callers — like the CSV import results table —
    can show the user what actually went wrong.
    """

    if response.ok:
        return

    detail = None

    try:
        body = response.json()
        if isinstance(body, dict):
            detail = body.get("detail") or body.get("message") or body.get("error")
        if detail is None:
            detail = body
    except ValueError:
        detail = response.text.strip() or None

    if detail:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason}: {detail}",
            response=response,
        )

    response.raise_for_status()


# ============================================================
# Helper Functions
# ============================================================

def _get_id(lead_json):
    """Handles either 'id' or 'lead_id' as the backend's key name."""
    return lead_json.get("id", lead_json.get("lead_id"))


def _to_tuple(lead_json):
    """
    Converts backend JSON into the existing tuple format.

    Existing tuple structure:
    (
        lead_id,
        company_name,
        industry,
        contact_name,
        email,
        phone,
        status,
        created_at
    )

    This is kept unchanged so the existing UI continues to work.
    """
    return (
        _get_id(lead_json),
        lead_json.get("company", ""),
        lead_json.get("industry", ""),
        lead_json.get("name", ""),
        lead_json.get("email", ""),
        lead_json.get("phone", ""),
        lead_json.get("status", "New"),
        lead_json.get("created_at", ""),
    )


# ============================================================
# Database Initialization
# ============================================================

def init_db():
    """
    No-op.

    The FastAPI backend manages the actual database.
    """
    pass


# ============================================================
# Add Lead
# ============================================================

def add_lead(
    company_name,
    industry,
    contact_name,
    email,
    phone,
    location="",
    company_size="",
    job_title="",
    budget_currency="",
    budget_amount="",
    lead_source="",
    purchase_timeline="",
    current_crm="",
    pain_points="",
    business_goals="",
    status="New",
    notes=""
):
    """
    Creates a new lead using the FastAPI backend.
    """

    payload = {
        "name": contact_name,
        "company": company_name,
        "email": email,
        "phone": phone,

        # New lead details
        "location": location,
        "industry": industry,
        "company_size": company_size,
        "job_title": job_title,

        # Budget
        "budget_currency": budget_currency,
        "budget_amount": budget_amount,

        # Sales information
        "lead_source": lead_source,
        "purchase_timeline": purchase_timeline,
        "current_crm": current_crm,
        "pain_points": pain_points,
        "business_goals": business_goals,

        # Existing fields
        "status": status,
        "notes": notes,
    }

    response = requests.post(
        f"{API_BASE}/leads/",
        json=payload
    )

    _raise_with_detail(response)

    return response.json()


# ============================================================
# Update Lead
# ============================================================

def update_lead(
    lead_id,
    company_name,
    industry,
    contact_name,
    email,
    phone,
    location="",
    company_size="",
    job_title="",
    budget_currency="",
    budget_amount="",
    lead_source="",
    purchase_timeline="",
    current_crm="",
    pain_points="",
    business_goals="",
    status="New",
    notes=""
):
    """
    Updates an existing lead using the FastAPI backend.
    """

    payload = {
        "name": contact_name,
        "company": company_name,
        "email": email,
        "phone": phone,

        # New lead details
        "location": location,
        "industry": industry,
        "company_size": company_size,
        "job_title": job_title,

        # Budget
        "budget_currency": budget_currency,
        "budget_amount": budget_amount,

        # Sales information
        "lead_source": lead_source,
        "purchase_timeline": purchase_timeline,
        "current_crm": current_crm,
        "pain_points": pain_points,
        "business_goals": business_goals,

        # Existing fields
        "status": status,
        "notes": notes,
    }

    response = requests.put(
        f"{API_BASE}/leads/{lead_id}",
        json=payload
    )

    _raise_with_detail(response)

    return response.json()


# ============================================================
# Get All Leads
# ============================================================

def get_all_leads_full(limit=100):
    """
    Fetches full lead JSON (not the trimmed tuple format) so callers can
    access fields like budget_amount and status directly. Requests up to
    `limit` records instead of relying on the backend's default of 10.
    """

    response = requests.get(
        f"{API_BASE}/leads/",
        params={"limit": limit},
    )

    _raise_with_detail(response)

    return response.json()


def get_all_leads(limit=100):
    """
    Fetches all leads from the FastAPI backend.

    Without an explicit `limit`, the backend defaults to returning only
    10 records — so leads added past the first 10 (e.g. from a bulk CSV
    import) would silently disappear from the Leads tab and Dashboard.
    The backend caps `limit` at 100, so that's the most we can request
    in one call.
    """

    response = requests.get(
        f"{API_BASE}/leads/",
        params={"limit": limit},
    )

    _raise_with_detail(response)

    leads_json = response.json()

    return [
        _to_tuple(lead)
        for lead in leads_json
    ]


# ============================================================
# Get Lead By ID
# ============================================================

def get_lead_by_id(lead_id):
    """
    Fetches a single lead by ID.
    """

    response = requests.get(
        f"{API_BASE}/leads/{lead_id}"
    )

    if response.status_code == 404:
        return None

    _raise_with_detail(response)

    return _to_tuple(response.json())


# ============================================================
# Get Full Lead Details
# ============================================================

def get_lead_details(lead_id):
    """
    Fetches the complete lead JSON from the backend.

    This is used when we need the new fields such as:
    location, company_size, budget, lead_source, etc.
    """

    response = requests.get(
        f"{API_BASE}/leads/{lead_id}"
    )

    if response.status_code == 404:
        return None

    _raise_with_detail(response)

    return response.json()


# ============================================================
# Find Duplicate Lead
# ============================================================

def find_duplicate_lead(email, phone):
    """
    Checks whether a lead with the same email or phone exists.
    """

    all_leads = get_all_leads()

    for lead in all_leads:

        existing_email = (lead[4] or "").lower().strip()
        existing_phone = (lead[5] or "").strip()

        if (
            existing_email == email.strip().lower()
            or existing_phone == phone.strip()
        ):
            return lead

    return None


# ============================================================
# Delete Lead
# ============================================================

def delete_lead(lead_id):
    response = requests.delete(
        f"{API_BASE}/leads/{lead_id}"
    )

    if response.status_code >= 400:
        raise Exception(
            f"Delete failed!\n"
            f"Lead ID: {lead_id}\n"
            f"Status Code: {response.status_code}\n"
            f"Backend Response: {response.text}"
        )

    return response.json()


# ============================================================
# Update Lead Status
# ============================================================

def update_lead_status(lead_id, status):
    """
    Updates only the status of an existing lead.

    The complete lead information is first fetched from the backend
    so that updating the status does not accidentally remove
    the newly added lead details.
    """

    current = get_lead_details(lead_id)

    if current is None:
        return

    payload = {
        "name": current.get("name", ""),
        "company": current.get("company", ""),
        "email": current.get("email"),
        "phone": current.get("phone"),

        # New lead details
        "location": current.get("location"),
        "industry": current.get("industry"),
        "company_size": current.get("company_size"),
        "job_title": current.get("job_title"),

        # Budget
        "budget_currency": current.get("budget_currency"),
        "budget_amount": current.get("budget_amount"),

        # Sales information
        "lead_source": current.get("lead_source"),
        "purchase_timeline": current.get("purchase_timeline"),
        "current_crm": current.get("current_crm"),
        "pain_points": current.get("pain_points"),
        "business_goals": current.get("business_goals"),

        # Updated status
        "status": status,

        # Existing notes
        "notes": current.get("notes"),
    }

    response = requests.put(
        f"{API_BASE}/leads/{lead_id}",
        json=payload
    )

    _raise_with_detail(response)