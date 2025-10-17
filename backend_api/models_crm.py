"""
IoT Multi-Rubro - CRM Models
=============================
Modelos de datos para sistema CRM integrado
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# ============================================
# CONTACT - Contacto General
# ============================================
class Contact(Base):
    """Modelo para gestión de contactos (clientes, leads, proveedores)."""
    
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información básica
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50))
    phone_secondary = Column(String(50), nullable=True)
    
    # Tipo y estado
    contact_type = Column(String(50), default="lead")  # lead, customer, supplier, partner
    status = Column(String(50), default="active")  # active, inactive, blocked
    
    # Información de negocio
    company = Column(String(200), nullable=True)
    position = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)  # rubro del cliente
    
    # Ubicación
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Argentina")
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Información adicional
    website = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # ["vip", "mayorista", etc]
    
    # Lead scoring y segmentación
    lead_score = Column(Integer, default=0)  # 0-100
    segment = Column(String(50), nullable=True)  # premium, standard, basic
    
    # Fuente de captación
    source = Column(String(100), nullable=True)  # website, demo, referral, etc
    source_details = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_date = Column(DateTime, nullable=True)
    
    # Relaciones
    leads = relationship("Lead", back_populates="contact", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="contact", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="contact", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contact {self.first_name} {self.last_name} ({self.email})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ============================================
# LEAD - Lead de Ventas
# ============================================
class Lead(Base):
    """Modelo para gestión de leads (contactos potenciales)."""
    
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    
    # Información del lead
    title = Column(String(200), nullable=False)  # "Interesado en sistema riego"
    description = Column(Text, nullable=True)
    
    # Estado en el pipeline
    stage = Column(String(50), default="new")  
    # Stages: new, contacted, qualified, demo, proposal, negotiation, won, lost
    
    status = Column(String(50), default="open")  # open, won, lost, abandoned
    
    # Valor y probabilidad
    estimated_value = Column(Float, default=0.0)
    probability = Column(Integer, default=10)  # 0-100%
    expected_close_date = Column(DateTime, nullable=True)
    
    # Clasificación
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    temperature = Column(String(20), default="cold")  # cold, warm, hot
    
    # Fuente y campaña
    source = Column(String(100), nullable=True)  # demo_bar, landing_riego, etc
    campaign = Column(String(100), nullable=True)
    
    # Necesidades y pain points
    needs = Column(Text, nullable=True)
    pain_points = Column(Text, nullable=True)
    budget = Column(Float, nullable=True)
    decision_maker = Column(String(200), nullable=True)
    
    # Competencia
    competitors = Column(JSON, default=list)
    
    # Asignación
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    lost_reason = Column(Text, nullable=True)
    
    # Relaciones
    contact = relationship("Contact", back_populates="leads")
    
    def __repr__(self):
        return f"<Lead {self.title} - {self.stage}>"


# ============================================
# OPPORTUNITY - Oportunidad de Venta
# ============================================
class Opportunity(Base):
    """Modelo para oportunidades de venta (negocios en proceso)."""
    
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    
    # Información básica
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Valores
    amount = Column(Float, nullable=False)
    monthly_recurring = Column(Float, default=0.0)  # MRR si es suscripción
    
    # Estado
    stage = Column(String(50), default="prospecting")
    # prospecting, qualification, proposal, negotiation, closed_won, closed_lost
    
    probability = Column(Integer, default=10)  # 0-100%
    
    # Fechas
    expected_close_date = Column(DateTime, nullable=True)
    actual_close_date = Column(DateTime, nullable=True)
    
    # Tipo de producto/servicio
    product_interest = Column(String(100), nullable=True)  # rubro específico
    plan_type = Column(String(50), nullable=True)  # basic, professional, enterprise
    
    # Competidores y contexto
    competitors = Column(JSON, default=list)
    next_steps = Column(Text, nullable=True)
    
    # Asignación
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    contact = relationship("Contact", back_populates="opportunities")
    
    def __repr__(self):
        return f"<Opportunity {self.name} - ${self.amount}>"


# ============================================
# INTERACTION - Interacción con Cliente
# ============================================
class Interaction(Base):
    """Modelo para registro de interacciones con clientes."""
    
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    
    # Tipo de interacción
    interaction_type = Column(String(50), nullable=False)
    # call, email, meeting, demo, whatsapp, visit, support
    
    # Dirección
    direction = Column(String(20), default="outbound")  # inbound, outbound
    
    # Contenido
    subject = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    outcome = Column(String(100), nullable=True)  # successful, no_answer, scheduled, etc
    
    # Duración (en minutos)
    duration = Column(Integer, nullable=True)
    
    # Seguimiento
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    
    # Asignación
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    contact = relationship("Contact", back_populates="interactions")
    
    def __repr__(self):
        return f"<Interaction {self.interaction_type} with Contact {self.contact_id}>"


# ============================================
# DEMO SESSION - Sesión de Demostración
# ============================================
class DemoSession(Base):
    """Modelo para tracking de sesiones de demo."""
    
    __tablename__ = "demo_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación
    session_id = Column(String(100), unique=True, index=True)
    rubro = Column(String(50), nullable=False)  # carniceria, bar, riego, etc
    
    # Información del visitante
    visitor_name = Column(String(200), nullable=True)
    visitor_email = Column(String(255), nullable=True)
    visitor_phone = Column(String(50), nullable=True)
    visitor_company = Column(String(200), nullable=True)
    
    # Geolocalización
    ip_address = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Actividad
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # Métricas de engagement
    pages_viewed = Column(Integer, default=0)
    features_tested = Column(JSON, default=list)
    interactions_count = Column(Integer, default=0)
    
    # Resultado
    converted_to_lead = Column(Boolean, default=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    interest_level = Column(String(20), nullable=True)  # low, medium, high
    
    # Source tracking
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Notas
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<DemoSession {self.session_id} - {self.rubro}>"


# ============================================
# CAMPAIGN - Campaña de Marketing
# ============================================
class Campaign(Base):
    """Modelo para campañas de marketing."""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información básica
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Tipo de campaña
    campaign_type = Column(String(50), nullable=False)
    # email, whatsapp, sms, social, ads, webinar
    
    # Estado
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    
    # Fechas
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Target
    target_audience = Column(String(100), nullable=True)  # segment o rubro
    target_count = Column(Integer, default=0)
    
    # Presupuesto
    budget = Column(Float, default=0.0)
    spent = Column(Float, default=0.0)
    
    # Métricas
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    
    # CTR y tasas
    ctr = Column(Float, default=0.0)  # Click-through rate
    conversion_rate = Column(Float, default=0.0)
    cost_per_lead = Column(Float, default=0.0)
    
    # Contenido
    message_template = Column(Text, nullable=True)
    call_to_action = Column(String(200), nullable=True)
    landing_page_url = Column(String(500), nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Campaign {self.name} - {self.campaign_type}>"
