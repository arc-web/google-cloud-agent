"""
Main FastAPI application for the Google Cloud Manager
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from app.core.config import settings
from app.core.auth import get_current_user
from app.services.ai_engine import AIEngine
from app.services.workflow_engine import WorkflowEngine
from app.services.google_cloud_service import GoogleCloudService
from app.services.monitoring_service import MonitoringService
from app.services.recommendation_service import RecommendationService
from app.services.gemini_service import GeminiService
from app.models.workflow import WorkflowRequest, WorkflowResponse, ApprovalRequest
from app.models.recommendation import Recommendation, CostAnalysis
from app.models.monitoring import ResourceMetrics, AlertConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ultra-Efficient Google Cloud Manager",
    description="AI-powered Google Cloud management with natural language processing and Gemini integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
ai_engine = AIEngine()
workflow_engine = WorkflowEngine()
gcp_service = GoogleCloudService()
monitoring_service = MonitoringService()
recommendation_service = RecommendationService()
gemini_service = GeminiService()

class NaturalLanguageRequest(BaseModel):
    """Request model for natural language commands"""
    command: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class NaturalLanguageResponse(BaseModel):
    """Response model for natural language processing"""
    interpreted_command: str
    confidence: float
    suggested_actions: List[str]
    estimated_impact: str
    requires_approval: bool

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: Dict[str, str]

class GeminiAnalysisRequest(BaseModel):
    """Request model for Gemini analysis"""
    project_id: str
    analysis_type: str  # "architecture", "costs", "security", "terraform", "code_review"
    requirements: Optional[str] = None
    code: Optional[str] = None
    context: Optional[str] = None

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with app information"""
    return {
        "message": "Ultra-Efficient Google Cloud Manager with Gemini Integration",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    services_status = {
        "ai_engine": "healthy" if ai_engine.is_healthy() else "unhealthy",
        "workflow_engine": "healthy" if workflow_engine.is_healthy() else "unhealthy",
        "gcp_service": "healthy" if gcp_service.is_healthy() else "unhealthy",
        "monitoring": "healthy" if monitoring_service.is_healthy() else "unhealthy",
        "gemini_service": "healthy" if gemini_service.is_healthy() else "unhealthy"
    }
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        services=services_status
    )

@app.post("/api/v1/natural-language", response_model=NaturalLanguageResponse)
async def process_natural_language(
    request: NaturalLanguageRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Process natural language commands and convert them to executable workflows
    """
    try:
        # Process the natural language command
        result = await ai_engine.process_command(
            command=request.command,
            context=request.context,
            user_id=current_user
        )
        
        return NaturalLanguageResponse(
            interpreted_command=result["interpreted_command"],
            confidence=result["confidence"],
            suggested_actions=result["suggested_actions"],
            estimated_impact=result["estimated_impact"],
            requires_approval=result["requires_approval"]
        )
    except Exception as e:
        logger.error(f"Error processing natural language command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/gemini/analyze", response_model=Dict[str, Any])
async def gemini_analysis(
    request: GeminiAnalysisRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Use Gemini to analyze Google Cloud resources and provide recommendations
    """
    try:
        if request.analysis_type == "architecture":
            result = await gemini_service.analyze_cloud_architecture(request.project_id)
        elif request.analysis_type == "costs":
            costs = await gcp_service.estimate_costs()
            result = await gemini_service.optimize_cloud_costs(costs)
        elif request.analysis_type == "security":
            result = await gemini_service.generate_security_policy(request.requirements or "")
        elif request.analysis_type == "terraform":
            result = await gemini_service.generate_terraform_config(request.requirements or "")
        elif request.analysis_type == "code_review":
            result = await gemini_service.code_review_and_suggestions(
                request.code or "", 
                request.context or ""
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        return result
    except Exception as e:
        logger.error(f"Error in Gemini analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/gemini/documentation", response_model=Dict[str, Any])
async def generate_documentation(
    code_or_config: str,
    doc_type: str = "README",
    current_user: str = Depends(get_current_user)
):
    """
    Generate documentation using Gemini
    """
    try:
        result = await gemini_service.generate_documentation(code_or_config, doc_type)
        return result
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """
    Create and execute a workflow
    """
    try:
        # Create workflow
        workflow = await workflow_engine.create_workflow(
            name=request.name,
            steps=request.steps,
            user_id=current_user
        )
        
        # Execute workflow in background if auto_execute is True
        if request.auto_execute:
            background_tasks.add_task(
                workflow_engine.execute_workflow,
                workflow_id=workflow.id
            )
        
        return WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            status=workflow.status,
            created_at=workflow.created_at,
            estimated_duration=workflow.estimated_duration
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get workflow details"""
    try:
        workflow = await workflow_engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            status=workflow.status,
            created_at=workflow.created_at,
            estimated_duration=workflow.estimated_duration
        )
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/approvals", response_model=Dict[str, str])
async def request_approval(
    request: ApprovalRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Request approval for a workflow or action
    """
    try:
        approval = await workflow_engine.request_approval(
            workflow_id=request.workflow_id,
            action=request.action,
            user_id=current_user,
            description=request.description
        )
        
        return {
            "approval_id": approval.id,
            "status": "pending",
            "message": "Approval request created successfully"
        }
    except Exception as e:
        logger.error(f"Error requesting approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/approvals/{approval_id}/approve")
async def approve_action(
    approval_id: str,
    current_user: str = Depends(get_current_user)
):
    """Approve an action"""
    try:
        result = await workflow_engine.approve_action(approval_id, current_user)
        return {"message": "Action approved successfully", "result": result}
    except Exception as e:
        logger.error(f"Error approving action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/approvals/{approval_id}/reject")
async def reject_action(
    approval_id: str,
    current_user: str = Depends(get_current_user)
):
    """Reject an action"""
    try:
        result = await workflow_engine.reject_action(approval_id, current_user)
        return {"message": "Action rejected", "result": result}
    except Exception as e:
        logger.error(f"Error rejecting action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/recommendations", response_model=List[Recommendation])
async def get_recommendations(
    current_user: str = Depends(get_current_user)
):
    """Get intelligent recommendations"""
    try:
        recommendations = await recommendation_service.get_recommendations(current_user)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/cost-analysis", response_model=CostAnalysis)
async def get_cost_analysis(
    current_user: str = Depends(get_current_user)
):
    """Get cost analysis and optimization suggestions"""
    try:
        analysis = await recommendation_service.get_cost_analysis(current_user)
        return analysis
    except Exception as e:
        logger.error(f"Error getting cost analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/resources", response_model=List[ResourceMetrics])
async def get_resource_metrics(
    current_user: str = Depends(get_current_user)
):
    """Get current resource metrics"""
    try:
        metrics = await monitoring_service.get_resource_metrics(current_user)
        return metrics
    except Exception as e:
        logger.error(f"Error getting resource metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/alerts", response_model=Dict[str, str])
async def create_alert(
    alert_config: AlertConfig,
    current_user: str = Depends(get_current_user)
):
    """Create a monitoring alert"""
    try:
        alert = await monitoring_service.create_alert(alert_config, current_user)
        return {
            "alert_id": alert.id,
            "message": "Alert created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/self-heal")
async def trigger_self_healing(
    current_user: str = Depends(get_current_user)
):
    """Trigger self-healing process"""
    try:
        result = await monitoring_service.trigger_self_healing(current_user)
        return {
            "message": "Self-healing process initiated",
            "issues_found": result["issues_found"],
            "issues_fixed": result["issues_fixed"]
        }
    except Exception as e:
        logger.error(f"Error triggering self-healing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects")
async def list_projects(
    current_user: str = Depends(get_current_user)
):
    """List Google Cloud projects"""
    try:
        projects = await gcp_service.list_projects()
        return {"projects": projects}
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/instances")
async def list_instances(
    project_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """List Compute Engine instances"""
    try:
        instances = await gcp_service.list_instances(project_id)
        return {"instances": instances}
    except Exception as e:
        logger.error(f"Error listing instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 