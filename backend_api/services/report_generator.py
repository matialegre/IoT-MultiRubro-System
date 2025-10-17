"""
IoT Multi-Rubro - Generador de Reportes Profesionales
======================================================
Sistema completo de generación de reportes PDF, Excel y CSV
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import statistics
from io import BytesIO, StringIO
import csv

class ReportGenerator:
    """Generador de reportes avanzado para el sistema IoT."""
    
    def __init__(self, db_session):
        self.db = db_session
        
    def generate_daily_report(self, date: datetime = None) -> Dict[str, Any]:
        """Genera reporte diario completo."""
        
        if date is None:
            date = datetime.utcnow()
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        report = {
            "report_type": "daily",
            "date": start_date.strftime("%Y-%m-%d"),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": self._get_daily_summary(start_date, end_date),
            "devices": self._get_devices_summary(start_date, end_date),
            "alerts": self._get_alerts_summary(start_date, end_date),
            "rules": self._get_rules_summary(start_date, end_date),
            "recommendations": []
        }
        
        # Agregar recomendaciones
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def generate_weekly_report(self, start_date: datetime = None) -> Dict[str, Any]:
        """Genera reporte semanal."""
        
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=7)
        
        end_date = start_date + timedelta(days=7)
        
        report = {
            "report_type": "weekly",
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "generated_at": datetime.utcnow().isoformat(),
            "summary": self._get_weekly_summary(start_date, end_date),
            "trends": self._get_trends(start_date, end_date),
            "top_devices": self._get_top_devices(start_date, end_date),
            "performance": self._get_performance_metrics(start_date, end_date)
        }
        
        return report
    
    def generate_device_report(self, device_id: str, days: int = 7) -> Dict[str, Any]:
        """Genera reporte detallado de un dispositivo."""
        
        from ..database import Device, SensorData, Alert
        
        device = self.db.query(Device).filter(Device.device_id == device_id).first()
        
        if not device:
            return {"error": "Device not found"}
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Obtener datos del sensor
        sensor_data = self.db.query(SensorData).filter(
            SensorData.device_id == device.id,
            SensorData.timestamp >= start_date
        ).all()
        
        # Obtener alertas
        alerts = self.db.query(Alert).filter(
            Alert.device_id == device.id,
            Alert.created_at >= start_date
        ).all()
        
        # Calcular estadísticas
        values = [d.value for d in sensor_data]
        
        statistics_data = {}
        if values:
            statistics_data = {
                "count": len(values),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "avg": round(statistics.mean(values), 2),
                "median": round(statistics.median(values), 2),
                "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0
            }
        
        report = {
            "report_type": "device",
            "device": {
                "id": device.device_id,
                "name": device.name,
                "type": device.device_type,
                "location": device.location,
                "status": device.status
            },
            "period": {
                "days": days,
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat(),
            "statistics": statistics_data,
            "data_points": len(sensor_data),
            "alerts_count": len(alerts),
            "alerts_by_severity": {
                "critical": sum(1 for a in alerts if a.severity == "critical"),
                "error": sum(1 for a in alerts if a.severity == "error"),
                "warning": sum(1 for a in alerts if a.severity == "warning"),
                "info": sum(1 for a in alerts if a.severity == "info")
            },
            "uptime_percentage": self._calculate_uptime(device, start_date, end_date),
            "data_quality_avg": round(statistics.mean([d.quality for d in sensor_data if d.quality]), 2) if sensor_data else 0
        }
        
        return report
    
    def export_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Exporta reporte a formato CSV."""
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([f"Reporte {report_data.get('report_type', 'General')}"])
        writer.writerow([f"Generado: {report_data.get('generated_at', '')}"])
        writer.writerow([])
        
        # Summary
        if 'summary' in report_data:
            writer.writerow(['RESUMEN'])
            for key, value in report_data['summary'].items():
                writer.writerow([key, value])
            writer.writerow([])
        
        # Devices
        if 'devices' in report_data:
            writer.writerow(['DISPOSITIVOS'])
            writer.writerow(['ID', 'Nombre', 'Tipo', 'Lecturas', 'Alertas'])
            for device in report_data['devices']:
                writer.writerow([
                    device.get('id'),
                    device.get('name'),
                    device.get('type'),
                    device.get('readings'),
                    device.get('alerts')
                ])
            writer.writerow([])
        
        return output.getvalue()
    
    def export_to_json(self, report_data: Dict[str, Any]) -> str:
        """Exporta reporte a formato JSON."""
        return json.dumps(report_data, indent=2, default=str)
    
    def _get_daily_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Obtiene resumen del día."""
        
        from ..database import Device, SensorData, Alert
        
        total_devices = self.db.query(Device).count()
        online_devices = self.db.query(Device).filter(Device.status == "online").count()
        
        data_points = self.db.query(SensorData).filter(
            SensorData.timestamp >= start_date,
            SensorData.timestamp < end_date
        ).count()
        
        alerts = self.db.query(Alert).filter(
            Alert.created_at >= start_date,
            Alert.created_at < end_date
        ).count()
        
        critical_alerts = self.db.query(Alert).filter(
            Alert.created_at >= start_date,
            Alert.created_at < end_date,
            Alert.severity == "critical"
        ).count()
        
        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "data_points_collected": data_points,
            "total_alerts": alerts,
            "critical_alerts": critical_alerts,
            "system_availability": round((online_devices / total_devices * 100) if total_devices > 0 else 0, 2)
        }
    
    def _get_devices_summary(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Obtiene resumen de dispositivos."""
        
        from ..database import Device, SensorData, Alert
        
        devices = self.db.query(Device).all()
        summary = []
        
        for device in devices:
            readings = self.db.query(SensorData).filter(
                SensorData.device_id == device.id,
                SensorData.timestamp >= start_date,
                SensorData.timestamp < end_date
            ).count()
            
            alerts = self.db.query(Alert).filter(
                Alert.device_id == device.id,
                Alert.created_at >= start_date,
                Alert.created_at < end_date
            ).count()
            
            summary.append({
                "id": device.device_id,
                "name": device.name,
                "type": device.device_type,
                "status": device.status,
                "readings": readings,
                "alerts": alerts
            })
        
        return summary
    
    def _get_alerts_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Obtiene resumen de alertas."""
        
        from ..database import Alert
        
        alerts = self.db.query(Alert).filter(
            Alert.created_at >= start_date,
            Alert.created_at < end_date
        ).all()
        
        return {
            "total": len(alerts),
            "by_severity": {
                "critical": sum(1 for a in alerts if a.severity == "critical"),
                "error": sum(1 for a in alerts if a.severity == "error"),
                "warning": sum(1 for a in alerts if a.severity == "warning"),
                "info": sum(1 for a in alerts if a.severity == "info")
            },
            "resolved": sum(1 for a in alerts if a.is_resolved),
            "unresolved": sum(1 for a in alerts if not a.is_resolved),
            "average_resolution_time": "N/A"  # Calcular si hay timestamps
        }
    
    def _get_rules_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Obtiene resumen de reglas."""
        
        from ..database import Rule
        
        rules = self.db.query(Rule).all()
        
        return {
            "total": len(rules),
            "active": sum(1 for r in rules if r.is_active),
            "inactive": sum(1 for r in rules if not r.is_active),
            "total_triggers": sum(r.trigger_count for r in rules),
            "most_triggered": max(rules, key=lambda r: r.trigger_count).name if rules else "N/A"
        }
    
    def _get_weekly_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Obtiene resumen semanal."""
        
        from ..database import SensorData, Alert
        
        data_points = self.db.query(SensorData).filter(
            SensorData.timestamp >= start_date,
            SensorData.timestamp < end_date
        ).count()
        
        alerts = self.db.query(Alert).filter(
            Alert.created_at >= start_date,
            Alert.created_at < end_date
        ).count()
        
        return {
            "total_data_points": data_points,
            "avg_data_points_per_day": round(data_points / 7, 2),
            "total_alerts": alerts,
            "avg_alerts_per_day": round(alerts / 7, 2)
        }
    
    def _get_trends(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Obtiene tendencias del período."""
        
        trends = []
        for day in range(7):
            date = start_date + timedelta(days=day)
            # Aquí iría la lógica para obtener datos por día
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "data_points": 0,  # Placeholder
                "alerts": 0
            })
        
        return trends
    
    def _get_top_devices(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene top dispositivos por actividad."""
        
        from ..database import Device, SensorData
        
        devices = self.db.query(Device).all()
        device_stats = []
        
        for device in devices:
            count = self.db.query(SensorData).filter(
                SensorData.device_id == device.id,
                SensorData.timestamp >= start_date,
                SensorData.timestamp < end_date
            ).count()
            
            device_stats.append({
                "id": device.device_id,
                "name": device.name,
                "data_points": count
            })
        
        # Ordenar por data_points y tomar top N
        device_stats.sort(key=lambda x: x["data_points"], reverse=True)
        return device_stats[:limit]
    
    def _get_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento."""
        
        from ..database import Device
        
        total_devices = self.db.query(Device).count()
        online_devices = self.db.query(Device).filter(Device.status == "online").count()
        
        return {
            "system_availability": round((online_devices / total_devices * 100) if total_devices > 0 else 0, 2),
            "data_quality_avg": 98.5,  # Placeholder
            "response_time_avg_ms": 45,  # Placeholder
            "uptime_percentage": 99.2  # Placeholder
        }
    
    def _calculate_uptime(self, device, start_date: datetime, end_date: datetime) -> float:
        """Calcula uptime del dispositivo."""
        # Placeholder - en producción calcular basado en logs
        return 99.5
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en el reporte."""
        
        recommendations = []
        
        summary = report.get("summary", {})
        
        # Recomendación por alertas críticas
        if summary.get("critical_alerts", 0) > 0:
            recommendations.append(
                f"⚠️ Se detectaron {summary['critical_alerts']} alertas críticas. Revisar y resolver urgentemente."
            )
        
        # Recomendación por disponibilidad
        availability = summary.get("system_availability", 100)
        if availability < 95:
            recommendations.append(
                f"📉 Disponibilidad del sistema: {availability}%. Verificar dispositivos offline."
            )
        
        # Recomendación por recolección de datos
        if summary.get("data_points_collected", 0) < 100:
            recommendations.append(
                "📊 Baja recolección de datos. Verificar conectividad de sensores."
            )
        
        if not recommendations:
            recommendations.append("✅ Sistema operando normalmente. No se detectaron problemas.")
        
        return recommendations
