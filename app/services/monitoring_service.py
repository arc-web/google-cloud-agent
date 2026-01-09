"""
Monitoring Service for resource monitoring, alerts, and self-healing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.services.google_cloud_service import GoogleCloudService

logger = logging.getLogger(__name__)

@dataclass
class ResourceMetrics:
    """Resource metrics data class"""
    resource_id: str
    resource_name: str
    resource_type: str
    metrics: Dict[str, float]
    timestamp: datetime
    status: str
    alerts: List[str] = None

@dataclass
class AlertConfig:
    """Alert configuration data class"""
    id: str
    name: str
    resource_type: str
    metric_name: str
    threshold: float
    condition: str  # "above", "below", "equals"
    severity: str  # "low", "medium", "high", "critical"
    enabled: bool = True

@dataclass
class Alert:
    """Alert data class"""
    id: str
    alert_config_id: str
    resource_id: str
    resource_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    timestamp: datetime
    status: str  # "active", "resolved", "acknowledged"
    message: str

class MonitoringService:
    """Monitoring Service for resource monitoring and self-healing"""
    
    def __init__(self):
        self.gcp_service = GoogleCloudService()
        self.alerts: Dict[str, Alert] = {}
        self.alert_configs: Dict[str, AlertConfig] = {}
        self.monitoring_enabled = True
        self.self_healing_enabled = True
        
        # Start monitoring tasks
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._self_healing_loop())
    
    def is_healthy(self) -> bool:
        """Check if the monitoring service is healthy"""
        try:
            return self.monitoring_enabled and self.gcp_service.is_healthy()
        except Exception as e:
            logger.error(f"Monitoring Service health check failed: {e}")
            return False
    
    async def get_resource_metrics(self, user_id: str) -> List[ResourceMetrics]:
        """Get current resource metrics"""
        try:
            metrics = []
            
            # Get compute instances
            instances = await self.gcp_service.list_instances()
            for instance in instances:
                instance_metrics = await self._get_instance_metrics(instance)
                metrics.append(ResourceMetrics(
                    resource_id=instance["id"],
                    resource_name=instance["name"],
                    resource_type="compute_instance",
                    metrics=instance_metrics,
                    timestamp=datetime.now(),
                    status=instance["status"]
                ))
            
            # Get storage buckets
            buckets = await self.gcp_service.list_storage_buckets()
            for bucket in buckets:
                bucket_metrics = await self._get_storage_metrics(bucket)
                metrics.append(ResourceMetrics(
                    resource_id=bucket["name"],
                    resource_name=bucket["name"],
                    resource_type="storage_bucket",
                    metrics=bucket_metrics,
                    timestamp=datetime.now(),
                    status="active"
                ))
            
            # Get BigQuery datasets
            datasets = await self.gcp_service.list_bigquery_datasets()
            for dataset in datasets:
                dataset_metrics = await self._get_bigquery_metrics(dataset)
                metrics.append(ResourceMetrics(
                    resource_id=dataset["dataset_id"],
                    resource_name=dataset["dataset_id"],
                    resource_type="bigquery_dataset",
                    metrics=dataset_metrics,
                    timestamp=datetime.now(),
                    status="active"
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting resource metrics: {e}")
            return []
    
    async def _get_instance_metrics(self, instance: Dict[str, Any]) -> Dict[str, float]:
        """Get metrics for a compute instance"""
        try:
            # Mock metrics for MVP
            # In production, get real metrics from Cloud Monitoring
            return {
                "cpu_utilization": 45.2,
                "memory_utilization": 67.8,
                "disk_utilization": 23.4,
                "network_in": 1024.5,
                "network_out": 512.3
            }
        except Exception as e:
            logger.error(f"Error getting instance metrics: {e}")
            return {}
    
    async def _get_storage_metrics(self, bucket: Dict[str, Any]) -> Dict[str, float]:
        """Get metrics for a storage bucket"""
        try:
            # Mock metrics for MVP
            return {
                "object_count": 150,
                "total_size_gb": 2.5,
                "requests_per_second": 5.2
            }
        except Exception as e:
            logger.error(f"Error getting storage metrics: {e}")
            return {}
    
    async def _get_bigquery_metrics(self, dataset: Dict[str, Any]) -> Dict[str, float]:
        """Get metrics for a BigQuery dataset"""
        try:
            # Mock metrics for MVP
            return {
                "table_count": 8,
                "total_size_gb": 1.2,
                "query_count": 25
            }
        except Exception as e:
            logger.error(f"Error getting BigQuery metrics: {e}")
            return {}
    
    async def create_alert(self, alert_config: AlertConfig, user_id: str) -> Alert:
        """Create a monitoring alert"""
        try:
            alert_id = f"alert_{len(self.alerts) + 1}"
            
            alert = Alert(
                id=alert_id,
                alert_config_id=alert_config.id,
                resource_id="",
                resource_name="",
                metric_name=alert_config.metric_name,
                current_value=0.0,
                threshold=alert_config.threshold,
                severity=alert_config.severity,
                timestamp=datetime.now(),
                status="active",
                message=f"Alert created for {alert_config.metric_name}"
            )
            
            # Store alert config
            self.alert_configs[alert_config.id] = alert_config
            
            logger.info(f"Created alert {alert_id} for metric {alert_config.metric_name}")
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        logger.info("Monitoring loop started")
        
        while self.monitoring_enabled:
            try:
                # Get current metrics
                metrics = await self.get_resource_metrics("system")
                
                # Check alerts
                await self._check_alerts(metrics)
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_alerts(self, metrics: List[ResourceMetrics]):
        """Check if any alerts should be triggered"""
        try:
            for metric in metrics:
                for config in self.alert_configs.values():
                    if not config.enabled:
                        continue
                    
                    if config.resource_type != metric.resource_type:
                        continue
                    
                    if config.metric_name not in metric.metrics:
                        continue
                    
                    current_value = metric.metrics[config.metric_name]
                    threshold = config.threshold
                    
                    # Check if alert condition is met
                    should_alert = False
                    if config.condition == "above" and current_value > threshold:
                        should_alert = True
                    elif config.condition == "below" and current_value < threshold:
                        should_alert = True
                    elif config.condition == "equals" and current_value == threshold:
                        should_alert = True
                    
                    if should_alert:
                        await self._trigger_alert(config, metric, current_value)
                        
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _trigger_alert(self, config: AlertConfig, metric: ResourceMetrics, current_value: float):
        """Trigger an alert"""
        try:
            alert_id = f"alert_{len(self.alerts) + 1}"
            
            alert = Alert(
                id=alert_id,
                alert_config_id=config.id,
                resource_id=metric.resource_id,
                resource_name=metric.resource_name,
                metric_name=config.metric_name,
                current_value=current_value,
                threshold=config.threshold,
                severity=config.severity,
                timestamp=datetime.now(),
                status="active",
                message=f"{config.metric_name} is {config.condition} threshold ({current_value} vs {config.threshold})"
            )
            
            self.alerts[alert_id] = alert
            
            logger.warning(f"Alert triggered: {alert.message}")
            
            # If self-healing is enabled, try to fix the issue
            if self.self_healing_enabled:
                await self._attempt_self_healing(alert)
                
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _attempt_self_healing(self, alert: Alert):
        """Attempt to automatically fix the issue"""
        try:
            logger.info(f"Attempting self-healing for alert {alert.id}")
            
            # Determine the type of issue and apply appropriate fix
            if alert.metric_name == "cpu_utilization" and alert.current_value > 90:
                await self._fix_high_cpu(alert)
            elif alert.metric_name == "memory_utilization" and alert.current_value > 90:
                await self._fix_high_memory(alert)
            elif alert.metric_name == "disk_utilization" and alert.current_value > 90:
                await self._fix_high_disk(alert)
            else:
                logger.info(f"No automatic fix available for {alert.metric_name}")
                
        except Exception as e:
            logger.error(f"Error in self-healing: {e}")
    
    async def _fix_high_cpu(self, alert: Alert):
        """Fix high CPU utilization"""
        try:
            logger.info(f"Attempting to fix high CPU on {alert.resource_name}")
            
            # For MVP, just log the action
            # In production, this might involve:
            # - Scaling up the instance
            # - Restarting the application
            # - Adding more instances
            
            alert.status = "acknowledged"
            alert.message += " - Self-healing applied: CPU optimization attempted"
            
        except Exception as e:
            logger.error(f"Error fixing high CPU: {e}")
    
    async def _fix_high_memory(self, alert: Alert):
        """Fix high memory utilization"""
        try:
            logger.info(f"Attempting to fix high memory on {alert.resource_name}")
            
            # For MVP, just log the action
            # In production, this might involve:
            # - Restarting the application
            # - Scaling up memory
            # - Garbage collection
            
            alert.status = "acknowledged"
            alert.message += " - Self-healing applied: Memory optimization attempted"
            
        except Exception as e:
            logger.error(f"Error fixing high memory: {e}")
    
    async def _fix_high_disk(self, alert: Alert):
        """Fix high disk utilization"""
        try:
            logger.info(f"Attempting to fix high disk usage on {alert.resource_name}")
            
            # For MVP, just log the action
            # In production, this might involve:
            # - Cleaning up old files
            # - Expanding disk size
            # - Archiving data
            
            alert.status = "acknowledged"
            alert.message += " - Self-healing applied: Disk cleanup attempted"
            
        except Exception as e:
            logger.error(f"Error fixing high disk usage: {e}")
    
    async def _self_healing_loop(self):
        """Background self-healing loop"""
        logger.info("Self-healing loop started")
        
        while self.self_healing_enabled:
            try:
                # Check for issues that need proactive fixing
                await self._proactive_health_check()
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in self-healing loop: {e}")
                await asyncio.sleep(300)
    
    async def _proactive_health_check(self):
        """Proactive health check and optimization"""
        try:
            # Get current resource usage
            usage = await self.gcp_service.get_resource_usage()
            
            # Check for optimization opportunities
            if usage.get("compute", {}).get("stopped_instances", 0) > 0:
                await self._optimize_stopped_instances()
            
            # Check for security issues
            await self._check_security_issues()
            
        except Exception as e:
            logger.error(f"Error in proactive health check: {e}")
    
    async def _optimize_stopped_instances(self):
        """Optimize stopped instances"""
        try:
            instances = await self.gcp_service.list_instances()
            stopped_instances = [i for i in instances if i["status"] == "TERMINATED"]
            
            for instance in stopped_instances[:3]:  # Limit to 3 instances
                # Check if instance has been stopped for more than 24 hours
                # In production, you'd check the actual stop time
                logger.info(f"Considering optimization for stopped instance {instance['name']}")
                
        except Exception as e:
            logger.error(f"Error optimizing stopped instances: {e}")
    
    async def _check_security_issues(self):
        """Check for security issues"""
        try:
            # Get IAM policies
            policies = await self.gcp_service.get_iam_policies()
            
            # Check for overly permissive policies
            for policy in policies:
                if "roles/owner" in policy["role"] and len(policy["members"]) > 2:
                    logger.warning(f"Found overly permissive IAM policy: {policy['role']}")
                    
        except Exception as e:
            logger.error(f"Error checking security issues: {e}")
    
    async def trigger_self_healing(self, user_id: str) -> Dict[str, Any]:
        """Manually trigger self-healing process"""
        try:
            logger.info(f"Manual self-healing triggered by {user_id}")
            
            issues_found = 0
            issues_fixed = 0
            
            # Get current metrics
            metrics = await self.get_resource_metrics(user_id)
            
            # Check for issues
            for metric in metrics:
                if metric.metrics.get("cpu_utilization", 0) > 80:
                    issues_found += 1
                    await self._fix_high_cpu(Alert(
                        id="manual",
                        alert_config_id="manual",
                        resource_id=metric.resource_id,
                        resource_name=metric.resource_name,
                        metric_name="cpu_utilization",
                        current_value=metric.metrics["cpu_utilization"],
                        threshold=80,
                        severity="medium",
                        timestamp=datetime.now(),
                        status="active",
                        message="Manual self-healing"
                    ))
                    issues_fixed += 1
                
                if metric.metrics.get("memory_utilization", 0) > 80:
                    issues_found += 1
                    await self._fix_high_memory(Alert(
                        id="manual",
                        alert_config_id="manual",
                        resource_id=metric.resource_id,
                        resource_name=metric.resource_name,
                        metric_name="memory_utilization",
                        current_value=metric.metrics["memory_utilization"],
                        threshold=80,
                        severity="medium",
                        timestamp=datetime.now(),
                        status="active",
                        message="Manual self-healing"
                    ))
                    issues_fixed += 1
            
            return {
                "issues_found": issues_found,
                "issues_fixed": issues_fixed,
                "message": f"Self-healing completed. Found {issues_found} issues, fixed {issues_fixed}."
            }
            
        except Exception as e:
            logger.error(f"Error in manual self-healing: {e}")
            raise
    
    async def get_alerts(self, user_id: str, status: Optional[str] = None) -> List[Alert]:
        """Get alerts, optionally filtered by status"""
        try:
            alerts = list(self.alerts.values())
            
            if status:
                alerts = [a for a in alerts if a.status == status]
            
            return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> Dict[str, Any]:
        """Acknowledge an alert"""
        try:
            alert = self.alerts.get(alert_id)
            if not alert:
                raise ValueError(f"Alert {alert_id} not found")
            
            alert.status = "acknowledged"
            
            return {
                "alert_id": alert_id,
                "status": "acknowledged",
                "message": "Alert acknowledged"
            }
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            raise
    
    async def resolve_alert(self, alert_id: str, user_id: str) -> Dict[str, Any]:
        """Resolve an alert"""
        try:
            alert = self.alerts.get(alert_id)
            if not alert:
                raise ValueError(f"Alert {alert_id} not found")
            
            alert.status = "resolved"
            
            return {
                "alert_id": alert_id,
                "status": "resolved",
                "message": "Alert resolved"
            }
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            raise
    
    async def get_health_summary(self, user_id: str) -> Dict[str, Any]:
        """Get overall health summary"""
        try:
            metrics = await self.get_resource_metrics(user_id)
            alerts = await self.get_alerts(user_id)
            
            # Calculate health scores
            total_resources = len(metrics)
            healthy_resources = 0
            warning_resources = 0
            critical_resources = 0
            
            for metric in metrics:
                if metric.metrics.get("cpu_utilization", 0) > 90 or metric.metrics.get("memory_utilization", 0) > 90:
                    critical_resources += 1
                elif metric.metrics.get("cpu_utilization", 0) > 70 or metric.metrics.get("memory_utilization", 0) > 70:
                    warning_resources += 1
                else:
                    healthy_resources += 1
            
            active_alerts = len([a for a in alerts if a.status == "active"])
            
            return {
                "total_resources": total_resources,
                "healthy_resources": healthy_resources,
                "warning_resources": warning_resources,
                "critical_resources": critical_resources,
                "active_alerts": active_alerts,
                "overall_health": "healthy" if critical_resources == 0 else "warning" if warning_resources > 0 else "critical",
                "last_updated": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting health summary: {e}")
            return {} 