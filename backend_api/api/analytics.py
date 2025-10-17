"""
IoT Multi-Rubro - Analytics API
================================
Advanced analytics and insights endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics

from ..database import SessionLocal, Device, SensorData, Alert, Rule
from ..config import SENSOR_LIMITS

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@router.get("/analytics/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    """Get comprehensive system analytics."""
    
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    # Device statistics
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == "online").count()
    
    # Data statistics
    data_24h = db.query(SensorData).filter(
        SensorData.timestamp >= last_24h
    ).count()
    
    data_7d = db.query(SensorData).filter(
        SensorData.timestamp >= last_7d
    ).count()
    
    # Alert statistics
    alerts_24h = db.query(Alert).filter(
        Alert.created_at >= last_24h
    ).count()
    
    critical_alerts = db.query(Alert).filter(
        and_(
            Alert.severity == "critical",
            Alert.is_resolved == False
        )
    ).count()
    
    # Rules statistics
    active_rules = db.query(Rule).filter(Rule.is_active == True).count()
    total_triggers_24h = db.query(func.sum(Rule.trigger_count)).scalar() or 0
    
    return {
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": total_devices - online_devices,
            "online_percentage": round((online_devices / total_devices * 100) if total_devices > 0 else 0, 2)
        },
        "data": {
            "last_24h": data_24h,
            "last_7d": data_7d,
            "rate_per_hour": round(data_24h / 24, 2) if data_24h > 0 else 0,
            "rate_per_minute": round(data_24h / (24 * 60), 2) if data_24h > 0 else 0
        },
        "alerts": {
            "last_24h": alerts_24h,
            "critical_unresolved": critical_alerts,
            "avg_per_day": round(data_7d / 7, 2) if data_7d > 0 else 0
        },
        "rules": {
            "total": db.query(Rule).count(),
            "active": active_rules,
            "triggers_24h": total_triggers_24h
        },
        "timestamp": now.isoformat()
    }

@router.get("/analytics/device/{device_id}")
def get_device_analytics(
    device_id: str,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific device."""
    
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    now = datetime.utcnow()
    start_time = now - timedelta(hours=hours)
    
    # Get sensor data
    data_points = db.query(SensorData).filter(
        and_(
            SensorData.device_id == device.id,
            SensorData.timestamp >= start_time
        )
    ).order_by(SensorData.timestamp).all()
    
    if not data_points:
        return {
            "device_id": device_id,
            "device_name": device.name,
            "statistics": None,
            "message": "No data available for this period"
        }
    
    values = [d.value for d in data_points]
    
    # Calculate statistics
    stats = {
        "count": len(values),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "avg": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        "first_value": round(values[0], 2),
        "last_value": round(values[-1], 2),
        "change": round(values[-1] - values[0], 2),
        "change_percentage": round(((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0, 2)
    }
    
    # Get sensor limits
    sensor_limits = SENSOR_LIMITS.get(device.device_type, {})
    
    # Calculate violations
    violations = 0
    if sensor_limits:
        min_limit = sensor_limits.get("min", float('-inf'))
        max_limit = sensor_limits.get("max", float('inf'))
        violations = sum(1 for v in values if v < min_limit or v > max_limit)
    
    # Get related alerts
    alerts = db.query(Alert).filter(
        and_(
            Alert.device_id == device.id,
            Alert.created_at >= start_time
        )
    ).count()
    
    return {
        "device_id": device_id,
        "device_name": device.name,
        "device_type": device.device_type,
        "period_hours": hours,
        "statistics": stats,
        "limits": sensor_limits,
        "violations": violations,
        "violation_percentage": round((violations / len(values) * 100) if values else 0, 2),
        "alerts_generated": alerts,
        "quality_avg": round(statistics.mean([d.quality for d in data_points if d.quality]), 2),
        "timestamp": now.isoformat()
    }

@router.get("/analytics/trends")
def get_trends(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get system trends over time."""
    
    now = datetime.utcnow()
    trends = []
    
    for day in range(days, 0, -1):
        date = now - timedelta(days=day)
        start = date.replace(hour=0, minute=0, second=0)
        end = date.replace(hour=23, minute=59, second=59)
        
        # Count data points
        data_count = db.query(SensorData).filter(
            and_(
                SensorData.timestamp >= start,
                SensorData.timestamp <= end
            )
        ).count()
        
        # Count alerts
        alert_count = db.query(Alert).filter(
            and_(
                Alert.created_at >= start,
                Alert.created_at <= end
            )
        ).count()
        
        # Count critical alerts
        critical_count = db.query(Alert).filter(
            and_(
                Alert.created_at >= start,
                Alert.created_at <= end,
                Alert.severity == "critical"
            )
        ).count()
        
        trends.append({
            "date": start.strftime("%Y-%m-%d"),
            "data_points": data_count,
            "alerts": alert_count,
            "critical_alerts": critical_count
        })
    
    return {
        "period_days": days,
        "trends": trends
    }

@router.get("/analytics/devices-ranking")
def get_devices_ranking(
    metric: str = Query("data_count", regex="^(data_count|alerts|avg_value)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get device ranking by different metrics."""
    
    devices = db.query(Device).all()
    rankings = []
    
    for device in devices:
        if metric == "data_count":
            count = db.query(SensorData).filter(
                SensorData.device_id == device.id
            ).count()
            value = count
        elif metric == "alerts":
            count = db.query(Alert).filter(
                Alert.device_id == device.id
            ).count()
            value = count
        elif metric == "avg_value":
            avg = db.query(func.avg(SensorData.value)).filter(
                SensorData.device_id == device.id
            ).scalar()
            value = round(avg, 2) if avg else 0
        
        rankings.append({
            "device_id": device.device_id,
            "device_name": device.name,
            "device_type": device.device_type,
            "value": value,
            "metric": metric
        })
    
    # Sort by value descending
    rankings.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "metric": metric,
        "rankings": rankings[:limit]
    }

@router.get("/analytics/alerts-by-severity")
def get_alerts_by_severity(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get alert distribution by severity."""
    
    now = datetime.utcnow()
    start_time = now - timedelta(days=days)
    
    severities = ["info", "warning", "error", "critical"]
    distribution = {}
    
    for severity in severities:
        count = db.query(Alert).filter(
            and_(
                Alert.severity == severity,
                Alert.created_at >= start_time
            )
        ).count()
        distribution[severity] = count
    
    total = sum(distribution.values())
    
    return {
        "period_days": days,
        "distribution": distribution,
        "total": total,
        "percentages": {
            severity: round((count / total * 100) if total > 0 else 0, 2)
            for severity, count in distribution.items()
        }
    }

@router.get("/analytics/system-health")
def get_system_health(db: Session = Depends(get_db)):
    """Get overall system health score."""
    
    # Calculate health metrics
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == "online").count()
    
    unresolved_critical = db.query(Alert).filter(
        and_(
            Alert.severity == "critical",
            Alert.is_resolved == False
        )
    ).count()
    
    inactive_rules = db.query(Rule).filter(Rule.is_active == False).count()
    total_rules = db.query(Rule).count()
    
    # Calculate health score (0-100)
    device_health = (online_devices / total_devices * 100) if total_devices > 0 else 100
    alert_health = max(0, 100 - (unresolved_critical * 10))  # -10 points per critical alert
    rule_health = ((total_rules - inactive_rules) / total_rules * 100) if total_rules > 0 else 100
    
    overall_health = (device_health + alert_health + rule_health) / 3
    
    # Determine status
    if overall_health >= 90:
        status = "excellent"
        color = "success"
    elif overall_health >= 70:
        status = "good"
        color = "info"
    elif overall_health >= 50:
        status = "fair"
        color = "warning"
    else:
        status = "poor"
        color = "danger"
    
    return {
        "health_score": round(overall_health, 2),
        "status": status,
        "color": color,
        "components": {
            "devices": {
                "score": round(device_health, 2),
                "online": online_devices,
                "total": total_devices
            },
            "alerts": {
                "score": round(alert_health, 2),
                "critical_unresolved": unresolved_critical
            },
            "rules": {
                "score": round(rule_health, 2),
                "active": total_rules - inactive_rules,
                "total": total_rules
            }
        },
        "recommendations": get_health_recommendations(device_health, alert_health, rule_health)
    }

def get_health_recommendations(device_health: float, alert_health: float, rule_health: float) -> List[str]:
    """Generate health recommendations."""
    recommendations = []
    
    if device_health < 90:
        recommendations.append("Check offline devices and connectivity")
    
    if alert_health < 70:
        recommendations.append("Review and resolve critical alerts")
    
    if rule_health < 80:
        recommendations.append("Activate or review inactive rules")
    
    if not recommendations:
        recommendations.append("System is operating optimally")
    
    return recommendations

@router.get("/analytics/export")
def export_analytics(
    format: str = Query("json", regex="^(json|csv)$"),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Export analytics data."""
    
    now = datetime.utcnow()
    start_time = now - timedelta(days=days)
    
    # Get all devices with their data
    devices = db.query(Device).all()
    export_data = []
    
    for device in devices:
        data_points = db.query(SensorData).filter(
            and_(
                SensorData.device_id == device.id,
                SensorData.timestamp >= start_time
            )
        ).all()
        
        if data_points:
            values = [d.value for d in data_points]
            export_data.append({
                "device_id": device.device_id,
                "device_name": device.name,
                "device_type": device.device_type,
                "data_points_count": len(data_points),
                "avg_value": round(statistics.mean(values), 2),
                "min_value": round(min(values), 2),
                "max_value": round(max(values), 2),
                "first_reading": data_points[0].timestamp.isoformat(),
                "last_reading": data_points[-1].timestamp.isoformat()
            })
    
    if format == "csv":
        # Return CSV format hint (frontend should handle conversion)
        return {
            "format": "csv",
            "data": export_data,
            "note": "Convert to CSV format on client side"
        }
    
    return {
        "format": "json",
        "period_days": days,
        "exported_at": now.isoformat(),
        "devices_count": len(export_data),
        "data": export_data
    }
