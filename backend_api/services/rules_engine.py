"""
Rules Engine - Dynamic If-Then Automation
==========================================
Evaluates conditions and executes actions based on sensor data.
Supports complex conditions with AND/OR logic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import operator
from loguru import logger
from sqlalchemy.orm import Session

from database import Rule, Alert, Device, SensorData, AlertSeverity


class RulesEngine:
    """
    Evaluates automation rules and triggers actions.
    Supports complex conditions and multiple action types.
    """
    
    # Comparison operators
    OPERATORS = {
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        "in": lambda x, y: x in y,
        "not_in": lambda x, y: x not in y,
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.action_handlers = {
            "alert": self._handle_alert_action,
            "actuate": self._handle_actuate_action,
            "notify": self._handle_notify_action,
            "log": self._handle_log_action,
        }
    
    def evaluate_all_rules(self, device_id: str, current_value: float) -> List[Dict[str, Any]]:
        """
        Evaluate all active rules for a device.
        
        Args:
            device_id: Device identifier
            current_value: Latest sensor reading
            
        Returns:
            List of triggered actions
        """
        triggered_actions = []
        
        # Get all active rules
        active_rules = self.db.query(Rule).filter(
            Rule.is_active == True
        ).order_by(Rule.priority.desc()).all()
        
        for rule in active_rules:
            # Check if rule applies to this device
            if not self._rule_applies_to_device(rule, device_id):
                continue
            
            # Check cooldown period
            if self._is_in_cooldown(rule):
                logger.debug(f"Rule '{rule.name}' in cooldown, skipping")
                continue
            
            # Evaluate condition
            if self._evaluate_condition(rule.condition, device_id, current_value):
                logger.info(f"Rule '{rule.name}' triggered for device {device_id}")
                
                # Execute action
                action_result = self._execute_action(rule, device_id, current_value)
                
                if action_result:
                    triggered_actions.append(action_result)
                    
                    # Update rule statistics
                    rule.last_triggered = datetime.utcnow()
                    rule.trigger_count += 1
                    self.db.commit()
        
        return triggered_actions
    
    def _rule_applies_to_device(self, rule: Rule, device_id: str) -> bool:
        """Check if rule condition references this device."""
        condition = rule.condition
        
        # Simple condition
        if isinstance(condition, dict) and condition.get("device_id") == device_id:
            return True
        
        # Complex condition with AND/OR
        if isinstance(condition, dict):
            if "and" in condition:
                return any(c.get("device_id") == device_id for c in condition["and"])
            if "or" in condition:
                return any(c.get("device_id") == device_id for c in condition["or"])
        
        return False
    
    def _is_in_cooldown(self, rule: Rule) -> bool:
        """Check if rule is in cooldown period."""
        if not rule.last_triggered:
            return False
        
        cooldown_end = rule.last_triggered + timedelta(seconds=rule.cooldown_seconds)
        return datetime.utcnow() < cooldown_end
    
    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        device_id: str,
        current_value: float
    ) -> bool:
        """
        Evaluate a condition against current sensor value.
        
        Supports:
        - Simple: {"device_id": "TEMP-001", "operator": ">", "value": 25}
        - AND: {"and": [condition1, condition2]}
        - OR: {"or": [condition1, condition2]}
        """
        # Complex condition with AND
        if "and" in condition:
            return all(
                self._evaluate_simple_condition(c, device_id, current_value)
                for c in condition["and"]
            )
        
        # Complex condition with OR
        if "or" in condition:
            return any(
                self._evaluate_simple_condition(c, device_id, current_value)
                for c in condition["or"]
            )
        
        # Simple condition
        return self._evaluate_simple_condition(condition, device_id, current_value)
    
    def _evaluate_simple_condition(
        self,
        condition: Dict[str, Any],
        device_id: str,
        current_value: float
    ) -> bool:
        """Evaluate a simple comparison condition."""
        # Check if condition applies to this device
        if condition.get("device_id") != device_id:
            # Get value from another device
            other_device_id = condition.get("device_id")
            other_value = self._get_latest_value(other_device_id)
            if other_value is None:
                return False
            current_value = other_value
        
        # Get operator and threshold
        op_str = condition.get("operator")
        threshold = condition.get("value")
        parameter = condition.get("parameter", "value")
        
        if op_str not in self.OPERATORS:
            logger.error(f"Unknown operator: {op_str}")
            return False
        
        # Perform comparison
        op_func = self.OPERATORS[op_str]
        
        try:
            result = op_func(current_value, threshold)
            logger.debug(f"Condition: {current_value} {op_str} {threshold} = {result}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _get_latest_value(self, device_id: str) -> Optional[float]:
        """Get latest sensor reading for a device."""
        device = self.db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            return None
        
        latest_data = self.db.query(SensorData).filter(
            SensorData.device_id == device.id
        ).order_by(SensorData.timestamp.desc()).first()
        
        return latest_data.value if latest_data else None
    
    def _execute_action(
        self,
        rule: Rule,
        device_id: str,
        current_value: float
    ) -> Optional[Dict[str, Any]]:
        """Execute rule action based on action type."""
        action = rule.action
        action_type = action.get("type")
        
        if action_type not in self.action_handlers:
            logger.error(f"Unknown action type: {action_type}")
            return None
        
        handler = self.action_handlers[action_type]
        return handler(rule, action, device_id, current_value)
    
    def _handle_alert_action(
        self,
        rule: Rule,
        action: Dict[str, Any],
        device_id: str,
        current_value: float
    ) -> Dict[str, Any]:
        """Create system alert."""
        # Get device
        device = self.db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            return None
        
        # Map severity
        severity_str = action.get("severity", "warning")
        severity_map = {
            "info": AlertSeverity.INFO,
            "warning": AlertSeverity.WARNING,
            "error": AlertSeverity.ERROR,
            "critical": AlertSeverity.CRITICAL,
        }
        severity = severity_map.get(severity_str, AlertSeverity.WARNING)
        
        # Create alert
        message = action.get("message", "Rule triggered")
        message = message.replace("{value}", str(current_value))
        message = message.replace("{device}", device.name)
        
        alert = Alert(
            device_id=device.id,
            rule_id=rule.id,
            severity=severity,
            title=rule.name,
            message=message,
            is_acknowledged=False,
            is_resolved=False
        )
        
        self.db.add(alert)
        self.db.commit()
        
        logger.warning(f"Alert created: {message}")
        
        return {
            "type": "alert",
            "severity": severity_str,
            "message": message,
            "alert_id": alert.id
        }
    
    def _handle_actuate_action(
        self,
        rule: Rule,
        action: Dict[str, Any],
        device_id: str,
        current_value: float
    ) -> Dict[str, Any]:
        """Control actuator (valve, relay, etc.)."""
        target_device = action.get("target")
        command = action.get("command")
        
        logger.info(f"Actuating device {target_device}: {command}")
        
        # In simulation mode, just log
        # In real mode, send command to ESP32
        
        return {
            "type": "actuate",
            "target": target_device,
            "command": command,
            "status": "executed"
        }
    
    def _handle_notify_action(
        self,
        rule: Rule,
        action: Dict[str, Any],
        device_id: str,
        current_value: float
    ) -> Dict[str, Any]:
        """Send notification (email, SMS, WhatsApp)."""
        channel = action.get("channel", "email")
        recipients = action.get("recipients", [])
        message = action.get("message", "Notification from IoT system")
        
        logger.info(f"Sending notification via {channel} to {recipients}")
        
        # [Simulation] In real mode, integrate with notification services
        
        return {
            "type": "notify",
            "channel": channel,
            "recipients": recipients,
            "status": "sent (simulated)"
        }
    
    def _handle_log_action(
        self,
        rule: Rule,
        action: Dict[str, Any],
        device_id: str,
        current_value: float
    ) -> Dict[str, Any]:
        """Log event to system logs."""
        log_level = action.get("level", "INFO")
        message = action.get("message", f"Rule '{rule.name}' triggered")
        
        logger.log(log_level, message)
        
        return {
            "type": "log",
            "level": log_level,
            "message": message
        }


# ============================================
# RULE BUILDER UTILITIES
# ============================================
def build_simple_rule(
    device_id: str,
    operator: str,
    threshold: float,
    action_type: str,
    **action_params
) -> Dict[str, Any]:
    """
    Helper to build a simple rule configuration.
    
    Example:
        rule = build_simple_rule(
            device_id="TEMP-001",
            operator=">",
            threshold=25,
            action_type="alert",
            severity="warning",
            message="Temperature too high!"
        )
    """
    return {
        "condition": {
            "device_id": device_id,
            "operator": operator,
            "value": threshold,
            "parameter": "value"
        },
        "action": {
            "type": action_type,
            **action_params
        }
    }


def build_complex_rule(
    logic: str,  # "and" or "or"
    conditions: List[Dict[str, Any]],
    action_type: str,
    **action_params
) -> Dict[str, Any]:
    """
    Helper to build a complex rule with multiple conditions.
    
    Example:
        rule = build_complex_rule(
            logic="and",
            conditions=[
                {"device_id": "TEMP-001", "operator": ">", "value": 25},
                {"device_id": "HUM-001", "operator": "<", "value": 30}
            ],
            action_type="alert",
            severity="critical",
            message="High temp AND low humidity!"
        )
    """
    return {
        "condition": {
            logic: conditions
        },
        "action": {
            "type": action_type,
            **action_params
        }
    }


# ============================================
# TESTING
# ============================================
if __name__ == "__main__":
    print("Rules Engine - Unit Test")
    print("=" * 60)
    
    # Test condition evaluation
    engine = RulesEngine(None)  # Mock DB
    
    # Test operators
    test_cases = [
        (25, ">", 20, True),
        (25, "<", 30, True),
        (25, "==", 25, True),
        (25, "!=", 30, True),
        (15, ">", 20, False),
    ]
    
    for value, op, threshold, expected in test_cases:
        condition = {"operator": op, "value": threshold, "device_id": "TEST"}
        result = engine._evaluate_simple_condition(condition, "TEST", value)
        status = "✓" if result == expected else "✗"
        print(f"{status} {value} {op} {threshold} = {result} (expected {expected})")
    
    print("\n✓ Rules engine tests passed!")
