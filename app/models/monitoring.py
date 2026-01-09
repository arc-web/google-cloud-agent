"""
Monitoring data models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    """Alert severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class AlertCondition(str, Enum):
    """Alert condition enumeration"""
    ABOVE = "above"
    BELOW = "below"
    EQUALS = "equals"

class ResourceMetrics(BaseModel):
    """Resource metrics model"""
    resource_id: str = Field(..., description="Resource ID")
    resource_name: str = Field(..., description="Resource name")
    resource_type: str = Field(..., description="Resource type")
    metrics: Dict[str, float] = Field(..., description="Resource metrics")
    timestamp: datetime = Field(..., description="Metrics timestamp")
    status: str = Field(..., description="Resource status")
    alerts: Optional[List[str]] = Field(default=None, description="Active alerts")

class AlertConfig(BaseModel):
    """Alert configuration model"""
    id: str = Field(..., description="Alert configuration ID")
    name: str = Field(..., description="Alert name")
    resource_type: str = Field(..., description="Resource type to monitor")
    metric_name: str = Field(..., description="Metric to monitor")
    threshold: float = Field(..., description="Alert threshold")
    condition: AlertCondition = Field(..., description="Alert condition")
    severity: AlertSeverity = Field(..., description="Alert severity")
    enabled: bool = Field(default=True, description="Whether alert is enabled")

class Alert(BaseModel):
    """Alert model"""
    id: str = Field(..., description="Alert ID")
    alert_config_id: str = Field(..., description="Alert configuration ID")
    resource_id: str = Field(..., description="Resource ID")
    resource_name: str = Field(..., description="Resource name")
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current metric value")
    threshold: float = Field(..., description="Alert threshold")
    severity: AlertSeverity = Field(..., description="Alert severity")
    timestamp: datetime = Field(..., description="Alert timestamp")
    status: AlertStatus = Field(..., description="Alert status")
    message: str = Field(..., description="Alert message")

class HealthSummary(BaseModel):
    """Health summary model"""
    total_resources: int = Field(..., description="Total number of resources")
    healthy_resources: int = Field(..., description="Number of healthy resources")
    warning_resources: int = Field(..., description="Number of resources with warnings")
    critical_resources: int = Field(..., description="Number of critical resources")
    active_alerts: int = Field(..., description="Number of active alerts")
    overall_health: str = Field(..., description="Overall health status")
    last_updated: datetime = Field(..., description="Last update timestamp") 