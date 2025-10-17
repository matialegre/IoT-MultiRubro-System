"""
Script para inicializar modelos CRM en la base de datos
========================================================
Crea las tablas del CRM y datos de ejemplo
"""

from database import Base, engine, SessionLocal
from models_crm import Contact, Lead, Opportunity, Interaction, DemoSession, Campaign
from datetime import datetime, timedelta
import random

def init_crm_tables():
    """Crear tablas del CRM."""
    print("Creando tablas del CRM...")
    
    # Importar modelos para que SQLAlchemy los registre
    from models_crm import Contact, Lead, Opportunity, Interaction, DemoSession, Campaign
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    print("✓ Tablas del CRM creadas")

def seed_crm_demo_data():
    """Poblar base de datos con datos de demostración del CRM."""
    
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        if db.query(Contact).count() > 0:
            print("⚠ Ya existen datos del CRM")
            return
        
        print("Poblando datos de demostración del CRM...")
        
        # Crear contactos de ejemplo
        contacts = [
            Contact(
                first_name="Juan",
                last_name="Pérez",
                email="juan.perez@example.com",
                phone="+54 11 4444-5555",
                company="Carnicería Don Juan",
                industry="carniceria",
                contact_type="lead",
                source="website",
                lead_score=75,
                city="Buenos Aires",
                country="Argentina"
            ),
            Contact(
                first_name="María",
                last_name="González",
                email="maria.gonzalez@bar.com",
                phone="+54 11 5555-6666",
                company="Bar La Esquina",
                industry="bar",
                contact_type="customer",
                source="referral",
                lead_score=90,
                city="Córdoba",
                country="Argentina"
            ),
            Contact(
                first_name="Carlos",
                last_name="Rodríguez",
                email="carlos@riego.com",
                phone="+54 11 6666-7777",
                company="Campos del Sur",
                industry="riego",
                contact_type="lead",
                source="demo",
                lead_score=65,
                city="Mendoza",
                country="Argentina"
            ),
            Contact(
                first_name="Ana",
                last_name="Martínez",
                email="ana.martinez@tienda.com",
                phone="+54 11 7777-8888",
                company="Boutique Ana",
                industry="tienda",
                contact_type="lead",
                source="google_ads",
                lead_score=55,
                city="Rosario",
                country="Argentina"
            ),
            Contact(
                first_name="Roberto",
                last_name="Fernández",
                email="roberto@clinica.com",
                phone="+54 11 8888-9999",
                company="Centro Médico Salud",
                industry="medico",
                contact_type="customer",
                source="website",
                lead_score=85,
                city="La Plata",
                country="Argentina"
            )
        ]
        
        for contact in contacts:
            db.add(contact)
        
        db.flush()  # Obtener IDs
        
        # Crear leads
        leads = [
            Lead(
                contact_id=contacts[0].id,
                title="Interesado en sistema de cadena de frío",
                description="Carnicería mediana, necesita control HACCP",
                stage="demo",
                estimated_value=15000.0,
                probability=70,
                source="demo_carniceria",
                priority="high"
            ),
            Lead(
                contact_id=contacts[2].id,
                title="Sistema de riego para 5 hectáreas",
                description="Cultivo de vid, necesita automatización",
                stage="proposal",
                estimated_value=25000.0,
                probability=60,
                source="demo_riego"
            ),
            Lead(
                contact_id=contacts[3].id,
                title="Control de tráfico para tienda",
                description="Quiere optimizar personal según flujo",
                stage="contacted",
                estimated_value=8000.0,
                probability=40,
                source="landing_tienda"
            )
        ]
        
        for lead in leads:
            db.add(lead)
        
        # Crear oportunidades
        opportunities = [
            Opportunity(
                contact_id=contacts[1].id,
                name="Upgrade sistema RFID - Bar La Esquina",
                description="Cliente actual quiere agregar 20 tarjetas más",
                amount=5000.0,
                monthly_recurring=800.0,
                stage="negotiation",
                probability=80,
                expected_close_date=datetime.utcnow() + timedelta(days=15),
                product_interest="bar",
                plan_type="professional"
            ),
            Opportunity(
                contact_id=contacts[4].id,
                name="Sistema de turnos - Centro Médico Salud",
                description="Implementación completa con WhatsApp",
                amount=12000.0,
                monthly_recurring=1500.0,
                stage="closed_won",
                probability=100,
                actual_close_date=datetime.utcnow() - timedelta(days=5),
                product_interest="medico",
                plan_type="enterprise"
            )
        ]
        
        for opp in opportunities:
            db.add(opp)
        
        # Crear interacciones
        interactions = [
            Interaction(
                contact_id=contacts[0].id,
                interaction_type="demo",
                subject="Demo del sistema de cadena de frío",
                description="Mostró gran interés, preguntó por integración HACCP",
                outcome="successful",
                duration=45,
                follow_up_required=True,
                follow_up_date=datetime.utcnow() + timedelta(days=2)
            ),
            Interaction(
                contact_id=contacts[1].id,
                interaction_type="call",
                subject="Seguimiento implementación",
                description="Cliente satisfecho, solicitó capacitación adicional",
                outcome="successful",
                duration=15
            ),
            Interaction(
                contact_id=contacts[2].id,
                interaction_type="email",
                subject="Envío de propuesta comercial",
                description="Propuesta enviada con 3 opciones de plan",
                outcome="successful",
                follow_up_required=True,
                follow_up_date=datetime.utcnow() + timedelta(days=5)
            )
        ]
        
        for interaction in interactions:
            db.add(interaction)
        
        # Crear sesiones de demo
        demo_sessions = [
            DemoSession(
                session_id="demo-001",
                rubro="carniceria",
                visitor_name="Pedro López",
                visitor_email="pedro@carniceria.com",
                visitor_phone="+54 11 1111-2222",
                visitor_company="Carnicería Central",
                started_at=datetime.utcnow() - timedelta(hours=3),
                ended_at=datetime.utcnow() - timedelta(hours=2, minutes=30),
                duration_seconds=1800,
                pages_viewed=12,
                features_tested=["temperature_monitor", "alerts", "reports"],
                interactions_count=15,
                converted_to_lead=False,
                interest_level="high",
                utm_source="google",
                utm_campaign="invierno_2025"
            ),
            DemoSession(
                session_id="demo-002",
                rubro="bar",
                visitor_name="Laura Sánchez",
                visitor_email="laura@bar.com",
                started_at=datetime.utcnow() - timedelta(days=1),
                ended_at=datetime.utcnow() - timedelta(days=1, hours=-1),
                duration_seconds=600,
                pages_viewed=5,
                features_tested=["rfid_system"],
                interactions_count=7,
                converted_to_lead=True,
                interest_level="medium",
                utm_source="facebook"
            ),
            DemoSession(
                session_id="demo-003",
                rubro="riego",
                visitor_name="Miguel Torres",
                visitor_email="miguel@campo.com",
                started_at=datetime.utcnow() - timedelta(hours=12),
                ended_at=datetime.utcnow() - timedelta(hours=11, minutes=15),
                duration_seconds=2700,
                pages_viewed=18,
                features_tested=["irrigation_control", "humidity_sensors", "automation"],
                interactions_count=22,
                converted_to_lead=True,
                lead_id=leads[1].id,
                interest_level="high",
                utm_source="google",
                utm_medium="cpc"
            )
        ]
        
        for session in demo_sessions:
            db.add(session)
        
        # Crear campaña de ejemplo
        campaign = Campaign(
            name="Campaña Verano 2025 - Riego",
            description="Campaña enfocada en sistemas de riego para temporada de verano",
            campaign_type="ads",
            status="active",
            start_date=datetime.utcnow() - timedelta(days=15),
            end_date=datetime.utcnow() + timedelta(days=45),
            target_audience="riego",
            target_count=500,
            budget=10000.0,
            spent=3500.0,
            impressions=12500,
            clicks=450,
            conversions=25,
            leads_generated=12,
            ctr=3.6,
            conversion_rate=5.5,
            cost_per_lead=291.67,
            call_to_action="Solicitar Demo Gratis",
            landing_page_url="/demo?rubro=riego&utm_campaign=verano2025"
        )
        
        db.add(campaign)
        
        db.commit()
        print("✓ Datos de demostración del CRM creados")
        print(f"  - {len(contacts)} contactos")
        print(f"  - {len(leads)} leads")
        print(f"  - {len(opportunities)} oportunidades")
        print(f"  - {len(interactions)} interacciones")
        print(f"  - {len(demo_sessions)} sesiones de demo")
        print(f"  - 1 campaña")
        
    except Exception as e:
        print(f"✗ Error creando datos de demostración: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  INICIALIZACIÓN CRM - Sistema IoT Multi-Rubro")
    print("="*60 + "\n")
    
    init_crm_tables()
    seed_crm_demo_data()
    
    print("\n✅ CRM inicializado correctamente!")
    print("\nPuedes acceder a:")
    print("  - API CRM: http://localhost:8000/api/crm/contacts")
    print("  - Pipeline: http://localhost:8000/api/crm/pipeline")
    print("  - Analytics: http://localhost:8000/api/crm/analytics/overview")
    print("  - Demo: http://localhost:8000/demo.html")
    print()
