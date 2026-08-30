from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from database.connection import get_db
from database.models import Lead, SalesInteraction, OutreachCampaign, SalesAnalytics

router = APIRouter(prefix="/analytics", tags=["Sales Analytics"])


# ---------- Pydantic Schemas ----------

class ConversionRateResponse(BaseModel):
    total_leads: int
    converted_leads: int
    conversion_rate_percent: float


class PipelineValueResponse(BaseModel):
    total_pipeline_value: float
    leads_with_value_recorded: int
    note: str


class SalesCycleKPIResponse(BaseModel):
    total_leads: int
    converted_leads: int
    total_interactions: int
    emails_sent: int
    meetings_logged: int
    average_sales_cycle_days: Optional[float]
    min_sales_cycle_days: Optional[int]
    max_sales_cycle_days: Optional[int]
    note: str


class SalesAnalyticsUpsertRequest(BaseModel):
    revenue_generated: Optional[float] = None
    conversion_status: Optional[str] = None


class SalesAnalyticsResponse(BaseModel):
    id: int
    lead_id: int
    revenue_generated: Optional[float]
    conversion_status: Optional[str]

    class Config:
        from_attributes = True


class PipelineByStageResponse(BaseModel):
    stage_counts: dict
    note: str


class AnalyticsSummaryResponse(BaseModel):
    total_leads: int
    converted_leads: int
    conversion_rate: float
    pipeline_value: float
    average_sales_cycle: Optional[float]


# ---------- 1. Conversion Rate ----------
@router.get("/conversion-rate", response_model=ConversionRateResponse)
def get_conversion_rate(db: Session = Depends(get_db)):
    total_leads = db.query(Lead).count()
    converted_leads = db.query(Lead).filter(Lead.status == "Converted").count()

    conversion_rate = round((converted_leads / total_leads) * 100, 2) if total_leads > 0 else 0.0

    return ConversionRateResponse(
        total_leads=total_leads,
        converted_leads=converted_leads,
        conversion_rate_percent=conversion_rate,
    )


# ---------- 2. Pipeline Value ----------
@router.get("/pipeline-value", response_model=PipelineValueResponse)
def get_pipeline_value(db: Session = Depends(get_db)):
    total_value = db.query(func.coalesce(func.sum(SalesAnalytics.revenue_generated), 0.0)).scalar()
    leads_with_value = db.query(SalesAnalytics).filter(SalesAnalytics.revenue_generated.isnot(None)).count()

    return PipelineValueResponse(
        total_pipeline_value=float(total_value or 0.0),
        leads_with_value_recorded=leads_with_value,
        note=(
            "Calculated from SalesAnalytics.revenue_generated. The project has no deal-amount "
            "field on Lead itself, so this value reflects only leads that have a SalesAnalytics "
            "record with revenue populated. It will read 0 until that table has data."
        ),
    )


# ---------- 3. Sales Cycle KPIs ----------
@router.get("/sales-cycle-kpis", response_model=SalesCycleKPIResponse)
def get_sales_cycle_kpis(db: Session = Depends(get_db)):
    total_leads = db.query(Lead).count()
    converted_leads = db.query(Lead).filter(Lead.status == "Converted").count()
    total_interactions = db.query(SalesInteraction).count()
    emails_sent = db.query(OutreachCampaign).filter(OutreachCampaign.campaign_status == "Sent").count()
    meetings_logged = db.query(SalesInteraction).filter(SalesInteraction.interaction_type == "Meeting").count()

    # Average / min / max sales cycle: days between a converted lead's created_at and its
    # most recent logged interaction, computed across all converted leads. This is an
    # approximation — the project has no explicit "deal closed" timestamp, so the latest
    # interaction for a converted lead is used as the closest available proxy for close date.
    converted = db.query(Lead).filter(Lead.status == "Converted").all()
    cycle_days = []
    for lead in converted:
        last_interaction = (
            db.query(SalesInteraction)
            .filter(SalesInteraction.lead_id == lead.id)
            .order_by(SalesInteraction.meeting_date.desc())
            .first()
        )
        if last_interaction and last_interaction.meeting_date and lead.created_at:
            delta = last_interaction.meeting_date - lead.created_at
            cycle_days.append(delta.days)

    avg_cycle = round(sum(cycle_days) / len(cycle_days), 1) if cycle_days else None
    min_cycle = min(cycle_days) if cycle_days else None
    max_cycle = max(cycle_days) if cycle_days else None

    return SalesCycleKPIResponse(
        total_leads=total_leads,
        converted_leads=converted_leads,
        total_interactions=total_interactions,
        emails_sent=emails_sent,
        meetings_logged=meetings_logged,
        average_sales_cycle_days=avg_cycle,
        min_sales_cycle_days=min_cycle,
        max_sales_cycle_days=max_cycle,
        note=(
            "Sales cycle metrics are approximated as days between a converted lead's "
            "created_at and its most recent logged SalesInteraction, since no explicit "
            "deal-close timestamp exists in the schema. Fields return null if no converted "
            "leads have logged interactions yet."
        ),
    )


# ---------- 4. Record/Update Revenue for a Lead ----------
# Minimal write path so pipeline-value has real data to sum. Creates a
# SalesAnalytics row if one doesn't exist for this lead yet, otherwise
# updates the existing one.
@router.post("/lead/{lead_id}", response_model=SalesAnalyticsResponse)
def upsert_lead_analytics(lead_id: int, payload: SalesAnalyticsUpsertRequest, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    record = db.query(SalesAnalytics).filter(SalesAnalytics.lead_id == lead_id).first()
    if not record:
        record = SalesAnalytics(lead_id=lead_id)
        db.add(record)

    update_fields = payload.dict(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


# ---------- 5. Pipeline / Leads by Stage (status) ----------
@router.get("/pipeline-by-stage", response_model=PipelineByStageResponse)
def get_pipeline_by_stage(db: Session = Depends(get_db)):
    results = (
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )
    stage_counts = {status or "Unspecified": count for status, count in results}

    return PipelineByStageResponse(
        stage_counts=stage_counts,
        note="Grouped by Lead.status, the only stage-representing field in the current schema.",
    )


# ---------- 6. Consolidated Analytics Summary ----------
@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    total_leads = db.query(Lead).count()
    converted_leads = db.query(Lead).filter(Lead.status == "Converted").count()
    conversion_rate = round((converted_leads / total_leads) * 100, 2) if total_leads > 0 else 0.0

    total_value = db.query(func.coalesce(func.sum(SalesAnalytics.revenue_generated), 0.0)).scalar()

    converted = db.query(Lead).filter(Lead.status == "Converted").all()
    cycle_days = []
    for lead in converted:
        last_interaction = (
            db.query(SalesInteraction)
            .filter(SalesInteraction.lead_id == lead.id)
            .order_by(SalesInteraction.meeting_date.desc())
            .first()
        )
        if last_interaction and last_interaction.meeting_date and lead.created_at:
            cycle_days.append((last_interaction.meeting_date - lead.created_at).days)
    avg_cycle = round(sum(cycle_days) / len(cycle_days), 1) if cycle_days else None

    return AnalyticsSummaryResponse(
        total_leads=total_leads,
        converted_leads=converted_leads,
        conversion_rate=conversion_rate,
        pipeline_value=float(total_value or 0.0),
        average_sales_cycle=avg_cycle,
    )