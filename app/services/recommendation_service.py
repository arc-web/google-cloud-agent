"""
Recommendation Service for intelligent recommendations and cost optimization
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.services.google_cloud_service import GoogleCloudService
from app.services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)

@dataclass
class Recommendation:
    """Recommendation data class"""
    id: str
    title: str
    description: str
    category: str  # "cost", "performance", "security", "best_practice"
    priority: str  # "low", "medium", "high", "critical"
    estimated_savings: Optional[float] = None
    estimated_impact: str = "medium"
    implementation_effort: str = "medium"
    status: str = "pending"  # "pending", "implemented", "dismissed"
    created_at: datetime = None
    tags: List[str] = None

@dataclass
class CostAnalysis:
    """Cost analysis data class"""
    total_monthly_cost: float
    cost_breakdown: Dict[str, float]
    cost_trend: str  # "increasing", "decreasing", "stable"
    optimization_opportunities: List[Dict[str, Any]]
    projected_savings: float
    currency: str = "USD"
    period: str = "monthly"

class RecommendationService:
    """Recommendation Service for intelligent recommendations"""
    
    def __init__(self):
        self.gcp_service = GoogleCloudService()
        self.monitoring_service = MonitoringService()
        self.recommendations: Dict[str, Recommendation] = {}
        self.recommendation_enabled = True
        
        # Start recommendation generation
        asyncio.create_task(self._recommendation_loop())
    
    def is_healthy(self) -> bool:
        """Check if the recommendation service is healthy"""
        try:
            return self.recommendation_enabled
        except Exception as e:
            logger.error(f"Recommendation Service health check failed: {e}")
            return False
    
    async def get_recommendations(self, user_id: str) -> List[Recommendation]:
        """Get intelligent recommendations for the user"""
        try:
            # Generate fresh recommendations
            await self._generate_recommendations(user_id)
            
            # Return all recommendations
            return list(self.recommendations.values())
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    async def get_cost_analysis(self, user_id: str) -> CostAnalysis:
        """Get cost analysis and optimization suggestions"""
        try:
            # Get current costs
            costs = await self.gcp_service.estimate_costs()
            
            # Get resource usage
            usage = await self.gcp_service.get_resource_usage()
            
            # Analyze cost optimization opportunities
            opportunities = await self._analyze_cost_opportunities(usage, costs)
            
            # Calculate projected savings
            projected_savings = sum(opp.get("estimated_savings", 0) for opp in opportunities)
            
            # Determine cost trend (mock for MVP)
            cost_trend = "stable"
            
            return CostAnalysis(
                total_monthly_cost=costs.get("total_monthly_cost", 0),
                cost_breakdown=costs.get("breakdown", {}),
                cost_trend=cost_trend,
                optimization_opportunities=opportunities,
                projected_savings=projected_savings
            )
            
        except Exception as e:
            logger.error(f"Error getting cost analysis: {e}")
            return CostAnalysis(
                total_monthly_cost=0,
                cost_breakdown={},
                cost_trend="unknown",
                optimization_opportunities=[],
                projected_savings=0
            )
    
    async def _generate_recommendations(self, user_id: str):
        """Generate intelligent recommendations"""
        try:
            # Clear existing recommendations
            self.recommendations.clear()
            
            # Get current state
            instances = await self.gcp_service.list_instances()
            buckets = await self.gcp_service.list_storage_buckets()
            datasets = await self.gcp_service.list_bigquery_datasets()
            usage = await self.gcp_service.get_resource_usage()
            health_summary = await self.monitoring_service.get_health_summary(user_id)
            
            # Generate cost optimization recommendations
            await self._generate_cost_recommendations(instances, buckets, datasets, usage)
            
            # Generate performance recommendations
            await self._generate_performance_recommendations(instances, health_summary)
            
            # Generate security recommendations
            await self._generate_security_recommendations(instances, buckets)
            
            # Generate best practice recommendations
            await self._generate_best_practice_recommendations(instances, buckets, datasets)
            
            logger.info(f"Generated {len(self.recommendations)} recommendations")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
    
    async def _generate_cost_recommendations(self, instances: List[Dict], buckets: List[Dict], datasets: List[Dict], usage: Dict):
        """Generate cost optimization recommendations"""
        try:
            # Check for stopped instances
            stopped_instances = [i for i in instances if i["status"] == "TERMINATED"]
            if stopped_instances:
                self.recommendations["cost_stopped_instances"] = Recommendation(
                    id="cost_stopped_instances",
                    title="Delete Stopped Instances",
                    description=f"You have {len(stopped_instances)} stopped instances that are still incurring storage costs. Consider deleting them to save money.",
                    category="cost",
                    priority="medium",
                    estimated_savings=len(stopped_instances) * 5,  # $5 per stopped instance
                    estimated_impact="medium",
                    implementation_effort="low",
                    created_at=datetime.now(),
                    tags=["compute", "cost-optimization"]
                )
            
            # Check for oversized instances
            oversized_instances = []
            for instance in instances:
                if instance["status"] == "RUNNING":
                    # Mock check for oversized instances
                    if instance.get("machine_type", "").startswith("e2-standard-4"):
                        oversized_instances.append(instance)
            
            if oversized_instances:
                self.recommendations["cost_oversized_instances"] = Recommendation(
                    id="cost_oversized_instances",
                    title="Optimize Instance Sizes",
                    description=f"You have {len(oversized_instances)} instances that may be oversized for their workload. Consider downsizing to save costs.",
                    category="cost",
                    priority="medium",
                    estimated_savings=len(oversized_instances) * 20,  # $20 per instance
                    estimated_impact="medium",
                    implementation_effort="medium",
                    created_at=datetime.now(),
                    tags=["compute", "cost-optimization"]
                )
            
            # Check for unused storage buckets
            if len(buckets) > 5:
                self.recommendations["cost_unused_buckets"] = Recommendation(
                    id="cost_unused_buckets",
                    title="Review Storage Buckets",
                    description=f"You have {len(buckets)} storage buckets. Review and delete unused buckets to reduce storage costs.",
                    category="cost",
                    priority="low",
                    estimated_savings=len(buckets) * 2,  # $2 per bucket
                    estimated_impact="low",
                    implementation_effort="low",
                    created_at=datetime.now(),
                    tags=["storage", "cost-optimization"]
                )
            
            # Check for unused BigQuery datasets
            if len(datasets) > 3:
                self.recommendations["cost_unused_datasets"] = Recommendation(
                    id="cost_unused_datasets",
                    title="Review BigQuery Datasets",
                    description=f"You have {len(datasets)} BigQuery datasets. Review and delete unused datasets to reduce costs.",
                    category="cost",
                    priority="low",
                    estimated_savings=len(datasets) * 5,  # $5 per dataset
                    estimated_impact="low",
                    implementation_effort="low",
                    created_at=datetime.now(),
                    tags=["bigquery", "cost-optimization"]
                )
                
        except Exception as e:
            logger.error(f"Error generating cost recommendations: {e}")
    
    async def _generate_performance_recommendations(self, instances: List[Dict], health_summary: Dict):
        """Generate performance recommendations"""
        try:
            # Check for performance issues
            if health_summary.get("critical_resources", 0) > 0:
                self.recommendations["performance_critical_resources"] = Recommendation(
                    id="performance_critical_resources",
                    title="Address Critical Performance Issues",
                    description=f"You have {health_summary['critical_resources']} resources with critical performance issues. Immediate action is required.",
                    category="performance",
                    priority="critical",
                    estimated_savings=None,
                    estimated_impact="high",
                    implementation_effort="high",
                    created_at=datetime.now(),
                    tags=["performance", "critical"]
                )
            
            if health_summary.get("warning_resources", 0) > 0:
                self.recommendations["performance_warning_resources"] = Recommendation(
                    id="performance_warning_resources",
                    title="Optimize Performance",
                    description=f"You have {health_summary['warning_resources']} resources with performance warnings. Consider optimization.",
                    category="performance",
                    priority="medium",
                    estimated_savings=None,
                    estimated_impact="medium",
                    implementation_effort="medium",
                    created_at=datetime.now(),
                    tags=["performance", "optimization"]
                )
            
            # Check for auto-scaling opportunities
            running_instances = [i for i in instances if i["status"] == "RUNNING"]
            if len(running_instances) > 2:
                self.recommendations["performance_autoscaling"] = Recommendation(
                    id="performance_autoscaling",
                    title="Implement Auto-scaling",
                    description=f"You have {len(running_instances)} running instances. Consider implementing auto-scaling for better performance and cost efficiency.",
                    category="performance",
                    priority="medium",
                    estimated_savings=len(running_instances) * 10,  # $10 per instance
                    estimated_impact="high",
                    implementation_effort="high",
                    created_at=datetime.now(),
                    tags=["performance", "autoscaling"]
                )
                
        except Exception as e:
            logger.error(f"Error generating performance recommendations: {e}")
    
    async def _generate_security_recommendations(self, instances: List[Dict], buckets: List[Dict]):
        """Generate security recommendations"""
        try:
            # Check for public buckets
            public_buckets = []
            for bucket in buckets:
                # Mock check for public buckets
                if bucket.get("name", "").startswith("public-"):
                    public_buckets.append(bucket)
            
            if public_buckets:
                self.recommendations["security_public_buckets"] = Recommendation(
                    id="security_public_buckets",
                    title="Secure Public Storage Buckets",
                    description=f"You have {len(public_buckets)} storage buckets that may be publicly accessible. Review and secure them.",
                    category="security",
                    priority="high",
                    estimated_savings=None,
                    estimated_impact="high",
                    implementation_effort="medium",
                    created_at=datetime.now(),
                    tags=["security", "storage"]
                )
            
            # Check for instances without proper security
            unsecured_instances = []
            for instance in instances:
                if instance["status"] == "RUNNING":
                    # Mock check for security issues
                    if not instance.get("network_interfaces", [{}])[0].get("external_ip"):
                        unsecured_instances.append(instance)
            
            if unsecured_instances:
                self.recommendations["security_instance_access"] = Recommendation(
                    id="security_instance_access",
                    title="Review Instance Security",
                    description=f"You have {len(unsecured_instances)} instances that may need security review. Check firewall rules and access controls.",
                    category="security",
                    priority="medium",
                    estimated_savings=None,
                    estimated_impact="medium",
                    implementation_effort="medium",
                    created_at=datetime.now(),
                    tags=["security", "compute"]
                )
            
            # General security recommendations
            self.recommendations["security_iam_review"] = Recommendation(
                id="security_iam_review",
                title="Review IAM Permissions",
                description="Regularly review IAM permissions to ensure least privilege access and remove unnecessary permissions.",
                category="security",
                priority="medium",
                estimated_savings=None,
                estimated_impact="medium",
                implementation_effort="low",
                created_at=datetime.now(),
                tags=["security", "iam"]
            )
                
        except Exception as e:
            logger.error(f"Error generating security recommendations: {e}")
    
    async def _generate_best_practice_recommendations(self, instances: List[Dict], buckets: List[Dict], datasets: List[Dict]):
        """Generate best practice recommendations"""
        try:
            # Backup recommendations
            if instances and len(instances) > 0:
                self.recommendations["best_practice_backups"] = Recommendation(
                    id="best_practice_backups",
                    title="Implement Backup Strategy",
                    description="Ensure you have a comprehensive backup strategy for your compute instances and data.",
                    category="best_practice",
                    priority="medium",
                    estimated_savings=None,
                    estimated_impact="medium",
                    implementation_effort="medium",
                    created_at=datetime.now(),
                    tags=["backup", "disaster-recovery"]
                )
            
            # Monitoring recommendations
            self.recommendations["best_practice_monitoring"] = Recommendation(
                id="best_practice_monitoring",
                title="Enhance Monitoring",
                description="Implement comprehensive monitoring and alerting for all your resources to ensure proactive issue detection.",
                category="best_practice",
                priority="medium",
                estimated_savings=None,
                estimated_impact="medium",
                implementation_effort="medium",
                created_at=datetime.now(),
                tags=["monitoring", "observability"]
            )
            
            # Documentation recommendations
            self.recommendations["best_practice_documentation"] = Recommendation(
                id="best_practice_documentation",
                title="Improve Documentation",
                description="Maintain up-to-date documentation for your infrastructure, including architecture diagrams and operational procedures.",
                category="best_practice",
                priority="low",
                estimated_savings=None,
                estimated_impact="low",
                implementation_effort="low",
                created_at=datetime.now(),
                tags=["documentation", "knowledge-management"]
            )
            
            # Tagging recommendations
            if instances or buckets or datasets:
                self.recommendations["best_practice_tagging"] = Recommendation(
                    id="best_practice_tagging",
                    title="Implement Resource Tagging",
                    description="Use consistent resource tagging to improve cost allocation, security, and operational efficiency.",
                    category="best_practice",
                    priority="low",
                    estimated_savings=None,
                    estimated_impact="low",
                    implementation_effort="low",
                    created_at=datetime.now(),
                    tags=["tagging", "organization"]
                )
                
        except Exception as e:
            logger.error(f"Error generating best practice recommendations: {e}")
    
    async def _analyze_cost_opportunities(self, usage: Dict, costs: Dict) -> List[Dict[str, Any]]:
        """Analyze cost optimization opportunities"""
        try:
            opportunities = []
            
            # Stopped instances opportunity
            stopped_count = usage.get("compute", {}).get("stopped_instances", 0)
            if stopped_count > 0:
                opportunities.append({
                    "type": "stopped_instances",
                    "description": f"Delete {stopped_count} stopped instances",
                    "estimated_savings": stopped_count * 5,
                    "effort": "low",
                    "priority": "medium"
                })
            
            # Storage optimization opportunity
            bucket_count = usage.get("storage", {}).get("buckets", 0)
            if bucket_count > 5:
                opportunities.append({
                    "type": "unused_buckets",
                    "description": f"Review and delete unused storage buckets",
                    "estimated_savings": bucket_count * 2,
                    "effort": "low",
                    "priority": "low"
                })
            
            # BigQuery optimization opportunity
            dataset_count = usage.get("database", {}).get("datasets", 0)
            if dataset_count > 3:
                opportunities.append({
                    "type": "unused_datasets",
                    "description": f"Review and delete unused BigQuery datasets",
                    "estimated_savings": dataset_count * 5,
                    "effort": "low",
                    "priority": "low"
                })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing cost opportunities: {e}")
            return []
    
    async def _recommendation_loop(self):
        """Background recommendation generation loop"""
        logger.info("Recommendation loop started")
        
        while self.recommendation_enabled:
            try:
                # Generate recommendations for system user
                await self._generate_recommendations("system")
                
                # Wait before next generation
                await asyncio.sleep(3600)  # Generate every hour
                
            except Exception as e:
                logger.error(f"Error in recommendation loop: {e}")
                await asyncio.sleep(3600)
    
    async def implement_recommendation(self, recommendation_id: str, user_id: str) -> Dict[str, Any]:
        """Implement a recommendation"""
        try:
            recommendation = self.recommendations.get(recommendation_id)
            if not recommendation:
                raise ValueError(f"Recommendation {recommendation_id} not found")
            
            # Update recommendation status
            recommendation.status = "implemented"
            
            # Log the implementation
            logger.info(f"Recommendation {recommendation_id} implemented by {user_id}")
            
            return {
                "recommendation_id": recommendation_id,
                "status": "implemented",
                "message": f"Recommendation '{recommendation.title}' has been implemented"
            }
            
        except Exception as e:
            logger.error(f"Error implementing recommendation: {e}")
            raise
    
    async def dismiss_recommendation(self, recommendation_id: str, user_id: str, reason: str = "") -> Dict[str, Any]:
        """Dismiss a recommendation"""
        try:
            recommendation = self.recommendations.get(recommendation_id)
            if not recommendation:
                raise ValueError(f"Recommendation {recommendation_id} not found")
            
            # Update recommendation status
            recommendation.status = "dismissed"
            
            # Log the dismissal
            logger.info(f"Recommendation {recommendation_id} dismissed by {user_id}: {reason}")
            
            return {
                "recommendation_id": recommendation_id,
                "status": "dismissed",
                "message": f"Recommendation '{recommendation.title}' has been dismissed"
            }
            
        except Exception as e:
            logger.error(f"Error dismissing recommendation: {e}")
            raise
    
    async def get_recommendation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get recommendation summary"""
        try:
            recommendations = list(self.recommendations.values())
            
            summary = {
                "total_recommendations": len(recommendations),
                "by_category": {
                    "cost": len([r for r in recommendations if r.category == "cost"]),
                    "performance": len([r for r in recommendations if r.category == "performance"]),
                    "security": len([r for r in recommendations if r.category == "security"]),
                    "best_practice": len([r for r in recommendations if r.category == "best_practice"])
                },
                "by_priority": {
                    "critical": len([r for r in recommendations if r.priority == "critical"]),
                    "high": len([r for r in recommendations if r.priority == "high"]),
                    "medium": len([r for r in recommendations if r.priority == "medium"]),
                    "low": len([r for r in recommendations if r.priority == "low"])
                },
                "by_status": {
                    "pending": len([r for r in recommendations if r.status == "pending"]),
                    "implemented": len([r for r in recommendations if r.status == "implemented"]),
                    "dismissed": len([r for r in recommendations if r.status == "dismissed"])
                },
                "total_estimated_savings": sum(r.estimated_savings or 0 for r in recommendations),
                "last_updated": datetime.now()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting recommendation summary: {e}")
            return {} 