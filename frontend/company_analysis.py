import requests
import streamlit as st

from database import get_all_leads_full

API_BASE = "http://127.0.0.1:8000"


def analyze_company(company_name, industry):
    """
    Calls the backend AI scoring API to generate a real AI-based
    company/lead analysis.

    Returns the same response structure expected by the UI.
    """

    # ---------------------------------------------------------
    # Step 1: Find the lead from backend
    # ---------------------------------------------------------
    try:
        # Uses get_all_leads_full() (limit=100) instead of a bare
        # GET request, so leads past the backend's default page
        # size of 10 (e.g. from a bulk CSV import) are still found.
        leads = get_all_leads_full()

    except requests.RequestException as e:
        return {
            "company_name": company_name,
            "industry": industry,
            "insight": "Unable to connect to the backend AI service.",
            "qualification_score": 0,
            "opportunity": f"Backend connection error: {str(e)}",
        }

    # ---------------------------------------------------------
    # Step 2: Find selected company
    # ---------------------------------------------------------
    selected_lead = None

    for lead in leads:
        if (
            lead.get("company", "").strip().lower()
            == company_name.strip().lower()
        ):
            selected_lead = lead
            break

    if selected_lead is None:
        return {
            "company_name": company_name,
            "industry": industry,
            "insight": "Lead details could not be found.",
            "qualification_score": 0,
            "opportunity": "Unable to analyze this lead.",
        }

    lead_id = selected_lead.get("id")

    if lead_id is None:
        lead_id = selected_lead.get("lead_id")

    # ---------------------------------------------------------
    # Step 3: Call backend AI scoring API
    # ---------------------------------------------------------
    try:
        ai_response = requests.post(
            f"{API_BASE}/analysis/generate/{lead_id}",
            timeout=120,
        )

        ai_response.raise_for_status()

        result = ai_response.json()

    except requests.RequestException as e:
        return {
            "company_name": company_name,
            "industry": industry,
            "insight": "AI analysis could not be completed.",
            "qualification_score": 0,
            "opportunity": f"AI service error: {str(e)}",
        }

    # ---------------------------------------------------------
    # Step 4: Convert backend AI response to UI format
    # ---------------------------------------------------------

    qualification_score = result.get(
        "qualification_score",
        0,
    )

    conversion_probability = result.get(
        "conversion_probability",
        0,
    )

    engagement_level = result.get(
        "engagement_level",
        "Unknown",
    )

    recommendation = result.get(
        "insight",
        "No recommendation available."
    )

    next_best_action = result.get(
        "opportunity",
        "No next action available."
    )

    # ---------------------------------------------------------
    # Step 5: Return real AI analysis
    # ---------------------------------------------------------

    return {
        "company_name": company_name,
        "industry": industry,
        "qualification_score": qualification_score,
        "conversion_probability": conversion_probability,
        "engagement_level": engagement_level,

        "insight": recommendation,
        "opportunity": next_best_action,

        "recommendation": recommendation,
        "next_best_action": next_best_action,
    }