"""
Workflow data models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    """Workflow status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    APPROVAL_REQUIRED = "approval_required"

class WorkflowStep(BaseModel):
    """Workflow step model"""
    step_number: int = Field(..., description="Step number in the workflow")
    action: str = Field(..., description="Action to perform")
    description: str = Field(..., description="Description of the step")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Step parameters")
    timeout: Optional[int] = Field(default=300, description="Step timeout in seconds")

class WorkflowRequest(BaseModel):
    """Workflow creation request"""
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(default="", description="Workflow description")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    auto_execute: bool = Field(default=False, description="Whether to execute immediately")
    requires_approval: bool = Field(default=False, description="Whether approval is required")

class WorkflowResponse(BaseModel):
    """Workflow response"""
    id: str = Field(..., description="Workflow ID")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    status: WorkflowStatus = Field(..., description="Workflow status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    estimated_duration: str = Field(..., description="Estimated duration")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    requires_approval: bool = Field(..., description="Whether approval is required")

class ApprovalRequest(BaseModel):
    """Approval request"""
    workflow_id: str = Field(..., description="Workflow ID")
    action: str = Field(..., description="Action requiring approval")
    description: str = Field(..., description="Description of the action")

class ApprovalResponse(BaseModel):
    """Approval response"""
    approval_id: str = Field(..., description="Approval ID")
    workflow_id: str = Field(..., description="Workflow ID")
    status: str = Field(..., description="Approval status")
    created_at: datetime = Field(..., description="Creation timestamp")
    approved_by: Optional[str] = Field(default=None, description="Approver")
    approved_at: Optional[datetime] = Field(default=None, description="Approval timestamp") 