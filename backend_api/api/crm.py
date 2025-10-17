"""
IoT Multi-Rubro - CRM API
==========================
Endpoints para gestión de CRM y captación de clientes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from ..database import SessionLocal
from ..models_crm import Contact, Lead, Opportunity, Interaction, DemoSession, Campaign

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# PYDANTIC SCHEMAS
# ============================================

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    source: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    contact_type: str
    status: str
    lead_score: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class LeadCreate(BaseModel):
    contact_id: int
    title: str
    description: Optional[str] = None
    estimated_value: float = 0.0
    source: Optional[str] = None

class OpportunityCreate(BaseModel):
    contact_id: int
    name: str
    amount: float
    product_interest: Optional[str] = None
    expected_close_date: Optional[datetime] = None

class InteractionCreate(BaseModel):
    contact_id: int
    interaction_type: str
    subject: Optional[str] = None
    description: Optional[str] = None
    outcome: Optional[str] = None

class DemoSessionCreate(BaseModel):
    rubro: str
    visitor_name: Optional[str] = None
    visitor_email: Optional[EmailStr] = None
    visitor_phone: Optional[str] = None
    visitor_company: Optional[str] = None

# ============================================
# CONTACTS ENDPOINTS
# ============================================

@router.get("/crm/contacts", response_model=List[ContactResponse])
def get_contacts(
    skip: int = 0,
    limit: int = 100,
    contact_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de contactos con filtros."""
    
    query = db.query(Contact)
    
    if contact_type:
        query = query.filter(Contact.contact_type == contact_type)
    
    if search:
        search_filter = or_(
            Contact.first_name.ilike(f"%{search}%"),
            Contact.last_name.ilike(f"%{search}%"),
            Contact.email.ilike(f"%{search}%"),
            Contact.company.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    contacts = query.order_by(Contact.created_at.desc()).offset(skip).limit(limit).all()
    
    return contacts

@router.post("/crm/contacts", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Crear nuevo contacto."""
    
    # Verificar si el email ya existe
    existing = db.query(Contact).filter(Contact.email == contact.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    
    return db_contact

@router.get("/crm/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """Obtener contacto por ID."""
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact

@router.put("/crm/contacts/{contact_id}")
def update_contact(contact_id: int, updates: dict, db: Session = Depends(get_db)):
    """Actualizar contacto."""
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in updates.items():
        if hasattr(contact, key):
            setattr(contact, key, value)
    
    contact.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contact)
    
    return {"success": True, "contact": contact}

@router.delete("/crm/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Eliminar contacto."""
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    
    return {"success": True, "message": "Contact deleted"}

# ============================================
# LEADS ENDPOINTS
# ============================================

@router.get("/crm/leads")
def get_leads(
    stage: Optional[str] = None,
    status: str = "open",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de leads con filtros."""
    
    query = db.query(Lead)
    
    if status:
        query = query.filter(Lead.status == status)
    
    if stage:
        query = query.filter(Lead.stage == stage)
    
    leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    
    return leads

@router.post("/crm/leads")
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Crear nuevo lead."""
    
    # Verificar que el contacto existe
    contact = db.query(Contact).filter(Contact.id == lead.contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db_lead = Lead(**lead.dict())
    db.add(db_lead)
    
    # Actualizar tipo de contacto
    contact.contact_type = "lead"
    contact.last_contact_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_lead)
    
    return db_lead

@router.put("/crm/leads/{lead_id}/stage")
def update_lead_stage(lead_id: int, stage: str, db: Session = Depends(get_db)):
    """Actualizar stage del lead (para pipeline)."""
    
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.stage = stage
    lead.updated_at = datetime.utcnow()
    
    # Si el stage es won, marcar como customer
    if stage == "won":
        lead.status = "won"
        lead.closed_at = datetime.utcnow()
        contact = db.query(Contact).filter(Contact.id == lead.contact_id).first()
        if contact:
            contact.contact_type = "customer"
    
    db.commit()
    db.refresh(lead)
    
    return lead

@router.get("/crm/pipeline")
def get_pipeline(db: Session = Depends(get_db)):
    """Obtener vista del pipeline de ventas."""
    
    stages = ["new", "contacted", "qualified", "demo", "proposal", "negotiation"]
    
    pipeline = {}
    total_value = 0
    
    for stage in stages:
        leads = db.query(Lead).filter(
            and_(Lead.stage == stage, Lead.status == "open")
        ).all()
        
        stage_value = sum(lead.estimated_value for lead in leads)
        total_value += stage_value
        
        pipeline[stage] = {
            "count": len(leads),
            "value": stage_value,
            "leads": [
                {
                    "id": lead.id,
                    "title": lead.title,
                    "contact": lead.contact.full_name if lead.contact else "N/A",
                    "value": lead.estimated_value,
                    "probability": lead.probability
                }
                for lead in leads
            ]
        }
    
    return {
        "pipeline": pipeline,
        "total_leads": sum(stage["count"] for stage in pipeline.values()),
        "total_value": total_value
    }

# ============================================
# OPPORTUNITIES ENDPOINTS
# ============================================

@router.get("/crm/opportunities")
def get_opportunities(
    stage: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener oportunidades de venta."""
    
    query = db.query(Opportunity)
    
    if stage:
        query = query.filter(Opportunity.stage == stage)
    
    opportunities = query.order_by(Opportunity.expected_close_date).offset(skip).limit(limit).all()
    
    return opportunities

@router.post("/crm/opportunities")
def create_opportunity(opportunity: OpportunityCreate, db: Session = Depends(get_db)):
    """Crear nueva oportunidad."""
    
    contact = db.query(Contact).filter(Contact.id == opportunity.contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db_opportunity = Opportunity(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    
    return db_opportunity

# ============================================
# INTERACTIONS ENDPOINTS
# ============================================

@router.get("/crm/interactions")
def get_interactions(
    contact_id: Optional[int] = None,
    interaction_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener historial de interacciones."""
    
    query = db.query(Interaction)
    
    if contact_id:
        query = query.filter(Interaction.contact_id == contact_id)
    
    if interaction_type:
        query = query.filter(Interaction.interaction_type == interaction_type)
    
    interactions = query.order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return interactions

@router.post("/crm/interactions")
def create_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    """Registrar nueva interacción."""
    
    contact = db.query(Contact).filter(Contact.id == interaction.contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db_interaction = Interaction(**interaction.dict())
    db.add(db_interaction)
    
    # Actualizar última fecha de contacto
    contact.last_contact_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_interaction)
    
    return db_interaction

# ============================================
# DEMO SESSIONS ENDPOINTS
# ============================================

@router.post("/crm/demo/start")
def start_demo_session(demo: DemoSessionCreate, db: Session = Depends(get_db)):
    """Iniciar nueva sesión de demo."""
    
    import uuid
    
    session = DemoSession(
        session_id=str(uuid.uuid4()),
        rubro=demo.rubro,
        visitor_name=demo.visitor_name,
        visitor_email=demo.visitor_email,
        visitor_phone=demo.visitor_phone,
        visitor_company=demo.visitor_company
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "success": True,
        "session_id": session.session_id,
        "demo_url": f"/demo?session={session.session_id}&rubro={demo.rubro}"
    }

@router.put("/crm/demo/{session_id}/activity")
def update_demo_activity(
    session_id: str,
    pages_viewed: int = 0,
    features_tested: List[str] = [],
    db: Session = Depends(get_db)
):
    """Actualizar actividad de la sesión de demo."""
    
    session = db.query(DemoSession).filter(DemoSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Demo session not found")
    
    session.pages_viewed += pages_viewed
    session.features_tested = list(set(session.features_tested + features_tested))
    session.interactions_count += 1
    
    db.commit()
    
    return {"success": True}

@router.post("/crm/demo/{session_id}/convert")
def convert_demo_to_lead(
    session_id: str,
    visitor_data: dict,
    db: Session = Depends(get_db)
):
    """Convertir sesión de demo en lead."""
    
    session = db.query(DemoSession).filter(DemoSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Demo session not found")
    
    # Crear o actualizar contacto
    email = visitor_data.get("email") or session.visitor_email
    existing_contact = db.query(Contact).filter(Contact.email == email).first()
    
    if existing_contact:
        contact = existing_contact
    else:
        contact = Contact(
            first_name=visitor_data.get("first_name", session.visitor_name or "Demo"),
            last_name=visitor_data.get("last_name", "User"),
            email=email,
            phone=visitor_data.get("phone", session.visitor_phone),
            company=visitor_data.get("company", session.visitor_company),
            industry=session.rubro,
            source="demo",
            contact_type="lead"
        )
        db.add(contact)
        db.flush()
    
    # Crear lead
    lead = Lead(
        contact_id=contact.id,
        title=f"Interesado en {session.rubro} desde demo",
        description=f"Generado desde sesión de demo. Engagement: {session.interactions_count} interacciones",
        stage="demo",
        source=f"demo_{session.rubro}",
        estimated_value=visitor_data.get("estimated_value", 0)
    )
    db.add(lead)
    db.flush()
    
    # Actualizar sesión
    session.converted_to_lead = True
    session.lead_id = lead.id
    session.interest_level = visitor_data.get("interest_level", "medium")
    
    db.commit()
    
    return {
        "success": True,
        "contact_id": contact.id,
        "lead_id": lead.id,
        "message": "Demo convertido exitosamente a lead"
    }

@router.get("/crm/demo/stats")
def get_demo_stats(days: int = 30, db: Session = Depends(get_db)):
    """Obtener estadísticas de demos."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(DemoSession).filter(
        DemoSession.started_at >= start_date
    ).all()
    
    total_sessions = len(sessions)
    conversions = sum(1 for s in sessions if s.converted_to_lead)
    
    by_rubro = {}
    for session in sessions:
        if session.rubro not in by_rubro:
            by_rubro[session.rubro] = {"count": 0, "conversions": 0}
        by_rubro[session.rubro]["count"] += 1
        if session.converted_to_lead:
            by_rubro[session.rubro]["conversions"] += 1
    
    return {
        "period_days": days,
        "total_sessions": total_sessions,
        "conversions": conversions,
        "conversion_rate": round((conversions / total_sessions * 100) if total_sessions > 0 else 0, 2),
        "by_rubro": by_rubro,
        "avg_duration": round(sum(s.duration_seconds for s in sessions) / total_sessions if total_sessions > 0 else 0, 2)
    }

# ============================================
# ANALYTICS CRM
# ============================================

@router.get("/crm/analytics/overview")
def get_crm_overview(db: Session = Depends(get_db)):
    """Obtener overview del CRM."""
    
    total_contacts = db.query(Contact).count()
    total_leads = db.query(Lead).filter(Lead.status == "open").count()
    total_customers = db.query(Contact).filter(Contact.contact_type == "customer").count()
    
    # Leads por stage
    leads_by_stage = db.query(
        Lead.stage,
        func.count(Lead.id).label("count"),
        func.sum(Lead.estimated_value).label("value")
    ).filter(Lead.status == "open").group_by(Lead.stage).all()
    
    # Conversión últimos 30 días
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_leads = db.query(Lead).filter(Lead.created_at >= thirty_days_ago).count()
    won_leads = db.query(Lead).filter(
        and_(Lead.created_at >= thirty_days_ago, Lead.status == "won")
    ).count()
    
    return {
        "total_contacts": total_contacts,
        "total_leads": total_leads,
        "total_customers": total_customers,
        "leads_by_stage": [
            {"stage": stage, "count": count, "value": float(value or 0)}
            for stage, count, value in leads_by_stage
        ],
        "conversion_rate_30d": round((won_leads / new_leads * 100) if new_leads > 0 else 0, 2),
        "new_leads_30d": new_leads,
        "won_leads_30d": won_leads
    }
