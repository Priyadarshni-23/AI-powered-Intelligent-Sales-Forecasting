from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from database.connection import get_db
from database.models import Lead, CRMSyncLog, SalesInteraction


# --------------------------------------------------
# CRM Field Mapping Functions
# --------------------------------------------------

def map_lead_to_salesforce(lead: Lead) -> dict:
    """Maps a SalesGenie Lead into a Salesforce-compatible Lead field structure."""
    return {
        "FirstName": lead.name.split(" ")[0] if lead.name else None,
        "LastName": lead.name.split(" ")[-1] if lead.name else "Unknown",
        "Company": lead.company or "Unknown",
        "Email": lead.email,
        "Phone": lead.phone,
        "Industry": lead.industry,
        "Status": lead.status or "Open - Not Contacted",
        "Description": lead.notes,
    }


def map_lead_to_zoho(lead: Lead) -> dict:
    """Maps a SalesGenie Lead into a Zoho CRM-compatible Lead field structure."""
    return {
        "First_Name": lead.name.split(" ")[0] if lead.name else None,
        "Last_Name": lead.name.split(" ")[-1] if lead.name else "Unknown",
        "Company": lead.company or "Unknown",
        "Email": lead.email,
        "Phone": lead.phone,
        "Industry": lead.industry,
        "Lead_Status": lead.status or "Not Contacted",
        "Description": lead.notes,
    }


router = APIRouter(prefix="/crm", tags=["CRM Integration"])

def map_interaction_to_salesforce(interaction: SalesInteraction) -> dict:
    """Maps a SalesInteraction into a Salesforce Task-compatible structure."""
    return {
        "Subject": interaction.meeting_title or interaction.interaction_type or "Interaction",
        "Type": interaction.interaction_type,
        "ActivityDate": interaction.meeting_date.isoformat() if interaction.meeting_date else None,
        "Description": interaction.interaction_notes,
        "WhoId_LeadId": interaction.lead_id,
    }


def map_interaction_to_zoho(interaction: SalesInteraction) -> dict:
    """Maps a SalesInteraction into a Zoho Activity-compatible structure."""
    return {
        "Activity_Type": interaction.interaction_type,
        "Subject": interaction.meeting_title or interaction.interaction_type or "Interaction",
        "Due_Date": interaction.meeting_date.isoformat() if interaction.meeting_date else None,
        "Description": interaction.interaction_notes,
        "Related_Lead_Id": interaction.lead_id,
    }

def map_lead_to_hubspot(lead: Lead) -> dict:
    """Maps a SalesGenie Lead into a HubSpot Contact-compatible structure."""
    return {
        "firstname": lead.name.split(" ")[0] if lead.name else None,
        "lastname": lead.name.split(" ")[-1] if lead.name else "Unknown",
        "company": lead.company or "Unknown",
        "email": lead.email,
        "phone": lead.phone,
        "industry": lead.industry,
        "lifecyclestage": lead.status or "lead",
        "notes_last_contacted": lead.notes,
    }


SALESFORCE_STAGE_MAP = {
    "New": "Prospecting",
    "Contacted": "Qualification",
    "Qualified": "Needs Analysis",
    "Converted": "Closed Won",
    "Lost": "Closed Lost",
}

ZOHO_STAGE_MAP = {
    "New": "Qualification",
    "Contacted": "Value Proposition",
    "Qualified": "Needs Analysis",
    "Converted": "Closed Won",
    "Lost": "Closed Lost",
}

HUBSPOT_STAGE_MAP = {
    "New": "leadin",
    "Contacted": "qualifiedtobuy",
    "Qualified": "presentationscheduled",
    "Converted": "closedwon",
    "Lost": "closedlost",
}


def map_status_to_hubspot_stage(status: Optional[str]) -> str:
    return HUBSPOT_STAGE_MAP.get(status, "leadin")


def map_status_to_salesforce_stage(status: Optional[str]) -> str:
    return SALESFORCE_STAGE_MAP.get(status, "Prospecting")


def map_status_to_zoho_stage(status: Optional[str]) -> str:
    return ZOHO_STAGE_MAP.get(status, "Qualification")
# Pydantic Models

class CRMSyncLogResponse(BaseModel):
    id: int
    lead_id: int
    crm_name: str
    sync_type: str
    sync_status: str
    records_synced: int
    error_message: Optional[str] = None
    synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CRMSyncLogUpdateRequest(BaseModel):
    crm_name: Optional[str] = None
    sync_type: Optional[str] = None
    sync_status: Optional[str] = None
    records_synced: Optional[int] = None
    error_message: Optional[str] = None

class CRMFieldMappingResponse(BaseModel):
    lead_id: int
    crm_name: str
    mapped_fields: dict

class CRMSyncRequest(BaseModel):
    crm_name: Optional[str] = "salesforce"

class CRMActionResponse(BaseModel):
    crm_name: str
    mapped_fields: dict
    sync_log: CRMSyncLogResponse

# --------------------------------------------------
# 1. POST /crm/sync/{lead_id}
# --------------------------------------------------

@router.post("/sync/{lead_id}", response_model=CRMSyncLogResponse)
def sync_lead_to_crm(
    lead_id: int,
    request: CRMSyncRequest = CRMSyncRequest(),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    crm_normalized = (request.crm_name or "salesforce").strip().lower()

    if crm_normalized == "salesforce":
        mapped_fields = map_lead_to_salesforce(lead)
        crm_display_name = "Salesforce"

    elif crm_normalized == "zoho":
        mapped_fields = map_lead_to_zoho(lead)
        crm_display_name = "Zoho"

    elif crm_normalized == "hubspot":
        mapped_fields = map_lead_to_hubspot(lead)
        crm_display_name = "HubSpot"

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported CRM '{request.crm_name}'. Use 'salesforce' or 'zoho', or 'hubspot'."
        )

    # Simulated sync — no real CRM API call
    sync_type = "Lead Export"
    sync_status = "Success"
    records_synced = 1
    error_message = None
    synced_at = datetime.now(timezone.utc)

    new_sync_log = CRMSyncLog(
        lead_id=lead_id,
        crm_name=crm_display_name,
        sync_type=sync_type,
        sync_status=sync_status,
        records_synced=records_synced,
        error_message=error_message,
        synced_at=synced_at,
    )

    db.add(new_sync_log)
    db.commit()
    db.refresh(new_sync_log)

    return new_sync_log

# --------------------------------------------------
# 5. GET /crm/mapping/{lead_id}
# --------------------------------------------------

@router.get("/mapping/{lead_id}", response_model=CRMFieldMappingResponse)
def preview_crm_mapping(
    lead_id: int,
    crm: str = "salesforce",
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    crm_normalized = crm.strip().lower()

    if crm_normalized == "salesforce":
        mapped_fields = map_lead_to_salesforce(lead)
        crm_display_name = "Salesforce"

    elif crm_normalized == "zoho":
        mapped_fields = map_lead_to_zoho(lead)
        crm_display_name = "Zoho"

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported CRM '{crm}'. Use 'salesforce' or 'zoho', or 'hubspot'."
        )

    return CRMFieldMappingResponse(
        lead_id=lead.id,
        crm_name=crm_display_name,
        mapped_fields=mapped_fields,
    )

# --------------------------------------------------
# 2. GET /crm/{lead_id}
# --------------------------------------------------

@router.get("/{lead_id}", response_model=list[CRMSyncLogResponse])
def get_crm_sync_logs(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    sync_logs = (
    db.query(CRMSyncLog)
    .filter(CRMSyncLog.lead_id == lead_id)
    .order_by(CRMSyncLog.created_at.desc())
    .all()
)
    return sync_logs


# --------------------------------------------------
# 3. PUT /crm/update/{sync_id}
# --------------------------------------------------

@router.put("/update/{sync_id}", response_model=CRMSyncLogResponse)
def update_crm_sync_log(
    sync_id: int,
    request: CRMSyncLogUpdateRequest,
    db: Session = Depends(get_db),
):
    sync_log = db.query(CRMSyncLog).filter(CRMSyncLog.id == sync_id).first()
    if not sync_log:
        raise HTTPException(status_code=404, detail="CRMSyncLog not found")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sync_log, key, value)

    db.commit()
    db.refresh(sync_log)

    return sync_log


# --------------------------------------------------
# 4. DELETE /crm/{sync_id}
# --------------------------------------------------

@router.delete("/{sync_id}")
def delete_crm_sync_log(sync_id: int, db: Session = Depends(get_db)):
    sync_log = db.query(CRMSyncLog).filter(CRMSyncLog.id == sync_id).first()
    if not sync_log:
        raise HTTPException(status_code=404, detail="CRMSyncLog not found")

    db.delete(sync_log)
    db.commit()

    return {"message": "CRM Sync Log deleted successfully"}

# --------------------------------------------------
# 6. POST /crm/sync-activity/{interaction_id}
# --------------------------------------------------

@router.post("/sync-activity/{interaction_id}", response_model=CRMActionResponse)
def sync_activity_to_crm(interaction_id: int, crm: str = "salesforce", db: Session = Depends(get_db)):
    interaction = db.query(SalesInteraction).filter(SalesInteraction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Sales interaction not found")

    crm_normalized = crm.strip().lower()

    if crm_normalized == "salesforce":
        mapped_fields = map_interaction_to_salesforce(interaction)
        crm_display_name = "Salesforce"
    elif crm_normalized == "zoho":
        mapped_fields = map_interaction_to_zoho(interaction)
        crm_display_name = "Zoho"
    elif crm_normalized == "hubspot":
        mapped_fields = {
            "hs_activity_type": interaction.interaction_type,
            "hs_meeting_title": interaction.meeting_title,
            "hs_timestamp": interaction.meeting_date.isoformat()
                if interaction.meeting_date else None,
            "hs_body": interaction.interaction_notes,
            "associated_lead_id": interaction.lead_id,
        }
        crm_display_name = "HubSpot"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported CRM '{crm}'. Use 'salesforce' or 'zoho', or 'hubspot'.")

    sync_log = CRMSyncLog(
        lead_id=interaction.lead_id,
        crm_name=crm_display_name,
        sync_type="Activity Sync",
        sync_status="Success",
        records_synced=1,
        error_message=None,
        synced_at=datetime.now(timezone.utc),
    )
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)

    return CRMActionResponse(crm_name=crm_display_name, mapped_fields=mapped_fields, sync_log=sync_log)


# --------------------------------------------------
# 7. POST /crm/sync-deal-stage/{lead_id}
# --------------------------------------------------

@router.post("/sync-deal-stage/{lead_id}", response_model=CRMActionResponse)
def sync_deal_stage_to_crm(lead_id: int, crm: str = "salesforce", db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    crm_normalized = crm.strip().lower()

    if crm_normalized == "salesforce":
        stage = map_status_to_salesforce_stage(lead.status)
        crm_display_name = "Salesforce"
        mapped_fields = {"StageName": stage, "LeadId": lead.id, "SourceStatus": lead.status}
    elif crm_normalized == "zoho":
        stage = map_status_to_zoho_stage(lead.status)
        crm_display_name = "Zoho"
        mapped_fields = {"Stage": stage, "Lead_Id": lead.id, "Source_Status": lead.status}
    elif crm_normalized == "hubspot":
        stage = map_status_to_hubspot_stage(lead.status)
        crm_display_name = "HubSpot"
        mapped_fields = {
            "dealstage": stage,
            "lead_id": lead.id,
            "source_status": lead.status,
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported CRM '{crm}'. Use 'salesforce' or 'zoho', 'hubspot'.")

    sync_log = CRMSyncLog(
        lead_id=lead.id,
        crm_name=crm_display_name,
        sync_type="Deal Stage Sync",
        sync_status="Success",
        records_synced=1,
        error_message=None,
        synced_at=datetime.now(timezone.utc),
    )
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)

    return CRMActionResponse(crm_name=crm_display_name, mapped_fields=mapped_fields, sync_log=sync_log)