"""
IoT Multi-Rubro - Reports API
==============================
Endpoints para generación y descarga de reportes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from io import BytesIO

from ..database import SessionLocal
from ..services.report_generator import ReportGenerator

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# REPORT GENERATION ENDPOINTS
# ============================================

@router.get("/reports/daily")
def generate_daily_report(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Generate comprehensive daily report."""
    
    generator = ReportGenerator(db)
    
    report_date = None
    if date:
        try:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    report = generator.generate_daily_report(report_date)
    
    return {
        "success": True,
        "report": report
    }

@router.get("/reports/weekly")
def generate_weekly_report(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Generate weekly report."""
    
    generator = ReportGenerator(db)
    
    report_start = None
    if start_date:
        try:
            report_start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    report = generator.generate_weekly_report(report_start)
    
    return {
        "success": True,
        "report": report
    }

@router.get("/reports/device/{device_id}")
def generate_device_report(
    device_id: str,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Generate detailed device report."""
    
    generator = ReportGenerator(db)
    report = generator.generate_device_report(device_id, days)
    
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    
    return {
        "success": True,
        "report": report
    }

@router.get("/reports/export/csv")
def export_report_csv(
    report_type: str = Query("daily", regex="^(daily|weekly)$"),
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Export report as CSV file."""
    
    generator = ReportGenerator(db)
    
    # Generate report based on type
    if report_type == "daily":
        report_date = datetime.strptime(date, "%Y-%m-%d") if date else None
        report_data = generator.generate_daily_report(report_date)
    else:
        start_date = datetime.strptime(date, "%Y-%m-%d") if date else None
        report_data = generator.generate_weekly_report(start_date)
    
    # Convert to CSV
    csv_content = generator.export_to_csv(report_data)
    
    # Create filename
    filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/reports/export/json")
def export_report_json(
    report_type: str = Query("daily", regex="^(daily|weekly|device)$"),
    device_id: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Export report as JSON file."""
    
    generator = ReportGenerator(db)
    
    # Generate report based on type
    if report_type == "daily":
        report_date = datetime.strptime(date, "%Y-%m-%d") if date else None
        report_data = generator.generate_daily_report(report_date)
    elif report_type == "weekly":
        start_date = datetime.strptime(date, "%Y-%m-%d") if date else None
        report_data = generator.generate_weekly_report(start_date)
    elif report_type == "device":
        if not device_id:
            raise HTTPException(status_code=400, detail="device_id required for device reports")
        report_data = generator.generate_device_report(device_id, days)
    
    # Convert to JSON
    json_content = generator.export_to_json(report_data)
    
    # Create filename
    filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/reports/summary")
def get_reports_summary(db: Session = Depends(get_db)):
    """Get summary of available reports and quick stats."""
    
    generator = ReportGenerator(db)
    
    # Get today's summary
    today_report = generator.generate_daily_report()
    
    # Get yesterday's summary for comparison
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_report = generator.generate_daily_report(yesterday)
    
    today_summary = today_report.get("summary", {})
    yesterday_summary = yesterday_report.get("summary", {})
    
    # Calculate changes
    def calculate_change(today_val, yesterday_val):
        if yesterday_val == 0:
            return 0
        return round(((today_val - yesterday_val) / yesterday_val * 100), 2)
    
    return {
        "today": today_summary,
        "yesterday": yesterday_summary,
        "changes": {
            "data_points": calculate_change(
                today_summary.get("data_points_collected", 0),
                yesterday_summary.get("data_points_collected", 0)
            ),
            "alerts": calculate_change(
                today_summary.get("total_alerts", 0),
                yesterday_summary.get("total_alerts", 0)
            ),
            "availability": round(
                today_summary.get("system_availability", 0) - yesterday_summary.get("system_availability", 0),
                2
            )
        },
        "available_reports": [
            {
                "type": "daily",
                "description": "Reporte diario completo con todas las métricas",
                "endpoint": "/api/reports/daily"
            },
            {
                "type": "weekly",
                "description": "Reporte semanal con tendencias y análisis",
                "endpoint": "/api/reports/weekly"
            },
            {
                "type": "device",
                "description": "Reporte detallado por dispositivo",
                "endpoint": "/api/reports/device/{device_id}"
            }
        ]
    }

@router.post("/reports/schedule")
def schedule_report(
    report_type: str,
    frequency: str,
    recipients: list[str],
    db: Session = Depends(get_db)
):
    """Schedule automatic report generation and delivery."""
    
    # [Simulación] En producción, usar scheduler real (Celery, APScheduler)
    return {
        "success": True,
        "message": "Report scheduled successfully",
        "schedule": {
            "report_type": report_type,
            "frequency": frequency,
            "recipients": recipients,
            "next_run": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
    }

@router.get("/reports/templates")
def get_report_templates():
    """Get available report templates."""
    
    templates = [
        {
            "id": "executive_summary",
            "name": "Resumen Ejecutivo",
            "description": "Reporte de alto nivel para gerencia",
            "includes": ["kpis", "trends", "highlights"]
        },
        {
            "id": "technical_detailed",
            "name": "Detalle Técnico",
            "description": "Reporte técnico completo para IT",
            "includes": ["all_devices", "all_alerts", "performance_metrics", "logs"]
        },
        {
            "id": "compliance",
            "name": "Cumplimiento HACCP",
            "description": "Reporte de cumplimiento normativo",
            "includes": ["temperature_logs", "violations", "corrective_actions"]
        },
        {
            "id": "energy_usage",
            "name": "Consumo Energético",
            "description": "Análisis de consumo y eficiencia energética",
            "includes": ["power_consumption", "cost_analysis", "optimization_suggestions"]
        }
    ]
    
    return {
        "templates": templates
    }
