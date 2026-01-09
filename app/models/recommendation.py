"""
Recommendation data models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class RecommendationCategory(str, Enum):
    """Recommendation category enumeration"""
    COST = "cost"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEST_PRACTICE = "best_practice"

class RecommendationPriority(str, Enum):
    """Recommendation priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecommendationStatus(str, Enum):
    """Recommendation status enumeration"""
    PENDING = "pending"
    IMPLEMENTED = "implemented"
    DISMISSED = "dismissed"

class Recommendation(BaseModel):
    """Recommendation model"""
    id: str = Field(..., description="Recommendation ID")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Recommendation description")
    category: RecommendationCategory = Field(..., description="Recommendation category")
    priority: RecommendationPriority = Field(..., description="Recommendation priority")
    estimated_savings: Optional[float] = Field(default=None, description="Estimated cost savings")
    estimated_impact: str = Field(default="medium", description="Estimated impact")
    implementation_effort: str = Field(default="medium", description="Implementation effort")
    status: RecommendationStatus = Field(default=RecommendationStatus.PENDING, description="Recommendation status")
    created_at: datetime = Field(..., description="Creation timestamp")
    tags: List[str] = Field(default=[], description="Recommendation tags")

class CostAnalysis(BaseModel):
    """Cost analysis model"""
    total_monthly_cost: float = Field(..., description="Total monthly cost")
    cost_breakdown: Dict[str, float] = Field(..., description="Cost breakdown by service")
    cost_trend: str = Field(..., description="Cost trend (increasing/decreasing/stable)")
    optimization_opportunities: List[Dict[str, Any]] = Field(..., description="Optimization opportunities")
    projected_savings: float = Field(..., description="Projected savings")
    currency: str = Field(default="USD", description="Currency")
    period: str = Field(default="monthly", description="Cost period")

class RecommendationSummary(BaseModel):
    """Recommendation summary model"""
    total_recommendations: int = Field(..., description="Total number of recommendations")
    by_category: Dict[str, int] = Field(..., description="Recommendations by category")
    by_priority: Dict[str, int] = Field(..., description="Recommendations by priority")
    by_status: Dict[str, int] = Field(..., description="Recommendations by status")
    total_estimated_savings: float = Field(..., description="Total estimated savings")
    last_updated: datetime = Field(..., description="Last update timestamp") 