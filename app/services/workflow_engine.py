"""
Workflow Engine for managing and executing workflows
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    APPROVAL_REQUIRED = "approval_required"

class ApprovalStatus(Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class WorkflowStep:
    """Workflow step data class"""
    step_id: str
    step_number: int
    action: str
    description: str
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class Workflow:
    """Workflow data class"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus
    user_id: str
    created_at: datetime
    updated_at: datetime
    estimated_duration: str
    requires_approval: bool
    approval_id: Optional[str] = None

@dataclass
class Approval:
    """Approval data class"""
    id: str
    workflow_id: str
    action: str
    description: str
    user_id: str
    status: ApprovalStatus
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

class WorkflowEngine:
    """Workflow Engine for managing and executing workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.approvals: Dict[str, Approval] = {}
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        
        # Start the workflow executor
        asyncio.create_task(self._workflow_executor())
    
    def is_healthy(self) -> bool:
        """Check if the workflow engine is healthy"""
        try:
            return self.is_running
        except Exception as e:
            logger.error(f"Workflow Engine health check failed: {e}")
            return False
    
    async def create_workflow(
        self, 
        name: str, 
        steps: List[Dict[str, Any]], 
        user_id: str,
        description: str = "",
        requires_approval: bool = False
    ) -> Workflow:
        """Create a new workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Convert steps to WorkflowStep objects
            workflow_steps = []
            for i, step_data in enumerate(steps, 1):
                step = WorkflowStep(
                    step_id=str(uuid.uuid4()),
                    step_number=i,
                    action=step_data.get("action", ""),
                    description=step_data.get("description", "")
                )
                workflow_steps.append(step)
            
            # Create workflow
            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                steps=workflow_steps,
                status=WorkflowStatus.PENDING,
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                estimated_duration="Variable",
                requires_approval=requires_approval
            )
            
            # Store workflow
            self.workflows[workflow_id] = workflow
            
            logger.info(f"Created workflow {workflow_id}: {name}")
            return workflow
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    async def list_workflows(self, user_id: Optional[str] = None) -> List[Workflow]:
        """List workflows, optionally filtered by user"""
        workflows = list(self.workflows.values())
        
        if user_id:
            workflows = [w for w in workflows if w.user_id == user_id]
        
        return sorted(workflows, key=lambda w: w.created_at, reverse=True)
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow"""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Check if approval is required
            if workflow.requires_approval and workflow.approval_id:
                approval = self.approvals.get(workflow.approval_id)
                if not approval or approval.status != ApprovalStatus.APPROVED:
                    raise ValueError("Workflow requires approval before execution")
            
            # Update workflow status
            workflow.status = WorkflowStatus.RUNNING
            workflow.updated_at = datetime.now()
            
            # Add to execution queue
            await self.execution_queue.put(workflow_id)
            
            logger.info(f"Queued workflow {workflow_id} for execution")
            
            return {
                "workflow_id": workflow_id,
                "status": "queued",
                "message": "Workflow queued for execution"
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise
    
    async def _workflow_executor(self):
        """Background task to execute workflows"""
        self.is_running = True
        logger.info("Workflow executor started")
        
        while self.is_running:
            try:
                # Get workflow from queue
                workflow_id = await asyncio.wait_for(
                    self.execution_queue.get(), 
                    timeout=1.0
                )
                
                # Execute workflow
                await self._execute_workflow_steps(workflow_id)
                
            except asyncio.TimeoutError:
                # No workflows in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in workflow executor: {e}")
    
    async def _execute_workflow_steps(self, workflow_id: str):
        """Execute the steps of a workflow"""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return
            
            logger.info(f"Executing workflow {workflow_id}")
            
            for step in workflow.steps:
                try:
                    # Update step status
                    step.status = "running"
                    step.start_time = datetime.now()
                    workflow.updated_at = datetime.now()
                    
                    # Execute step
                    result = await self._execute_step(step)
                    
                    # Update step with result
                    step.status = "completed"
                    step.result = result
                    step.end_time = datetime.now()
                    
                    logger.info(f"Completed step {step.step_number} of workflow {workflow_id}")
                    
                except Exception as e:
                    # Step failed
                    step.status = "failed"
                    step.error = str(e)
                    step.end_time = datetime.now()
                    workflow.status = WorkflowStatus.FAILED
                    workflow.updated_at = datetime.now()
                    
                    logger.error(f"Step {step.step_number} failed in workflow {workflow_id}: {e}")
                    break
            
            # Update workflow status if all steps completed
            if workflow.status != WorkflowStatus.FAILED:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.updated_at = datetime.now()
                logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing workflow steps: {e}")
            # Update workflow status to failed
            workflow = await self.get_workflow(workflow_id)
            if workflow:
                workflow.status = WorkflowStatus.FAILED
                workflow.updated_at = datetime.now()
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            # Simulate step execution based on action type
            if step.action == "validate_permissions":
                return await self._validate_permissions()
            elif step.action == "validate_resources":
                return await self._validate_resources()
            elif step.action == "execute_operation":
                return await self._execute_operation()
            elif step.action == "verify_result":
                return await self._verify_result()
            elif step.action == "validate_bucket":
                return await self._validate_bucket()
            elif step.action == "execute_storage_operation":
                return await self._execute_storage_operation()
            elif step.action == "verify_storage":
                return await self._verify_storage()
            elif step.action == "validate_database":
                return await self._validate_database()
            elif step.action == "execute_database_operation":
                return await self._execute_database_operation()
            elif step.action == "verify_database":
                return await self._verify_database()
            elif step.action == "setup_monitoring":
                return await self._setup_monitoring()
            elif step.action == "create_alerts":
                return await self._create_alerts()
            elif step.action == "verify_monitoring":
                return await self._verify_monitoring()
            elif step.action == "audit_current_state":
                return await self._audit_current_state()
            elif step.action == "apply_security_changes":
                return await self._apply_security_changes()
            elif step.action == "verify_security":
                return await self._verify_security()
            else:
                # Default action
                return {"status": "completed", "message": f"Executed {step.action}"}
                
        except Exception as e:
            logger.error(f"Error executing step {step.action}: {e}")
            raise
    
    # Step execution methods (simulated for MVP)
    async def _validate_permissions(self) -> Dict[str, Any]:
        """Validate user permissions"""
        await asyncio.sleep(1)  # Simulate processing time
        return {"status": "success", "message": "Permissions validated"}
    
    async def _validate_resources(self) -> Dict[str, Any]:
        """Validate available resources"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Resources validated"}
    
    async def _execute_operation(self) -> Dict[str, Any]:
        """Execute the main operation"""
        await asyncio.sleep(2)
        return {"status": "success", "message": "Operation executed successfully"}
    
    async def _verify_result(self) -> Dict[str, Any]:
        """Verify the operation result"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Result verified"}
    
    async def _validate_bucket(self) -> Dict[str, Any]:
        """Validate storage bucket"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Bucket validated"}
    
    async def _execute_storage_operation(self) -> Dict[str, Any]:
        """Execute storage operation"""
        await asyncio.sleep(2)
        return {"status": "success", "message": "Storage operation completed"}
    
    async def _verify_storage(self) -> Dict[str, Any]:
        """Verify storage operation"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Storage operation verified"}
    
    async def _validate_database(self) -> Dict[str, Any]:
        """Validate database"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Database validated"}
    
    async def _execute_database_operation(self) -> Dict[str, Any]:
        """Execute database operation"""
        await asyncio.sleep(3)
        return {"status": "success", "message": "Database operation completed"}
    
    async def _verify_database(self) -> Dict[str, Any]:
        """Verify database operation"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Database operation verified"}
    
    async def _setup_monitoring(self) -> Dict[str, Any]:
        """Set up monitoring"""
        await asyncio.sleep(2)
        return {"status": "success", "message": "Monitoring setup completed"}
    
    async def _create_alerts(self) -> Dict[str, Any]:
        """Create monitoring alerts"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Alerts created"}
    
    async def _verify_monitoring(self) -> Dict[str, Any]:
        """Verify monitoring setup"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Monitoring verified"}
    
    async def _audit_current_state(self) -> Dict[str, Any]:
        """Audit current security state"""
        await asyncio.sleep(2)
        return {"status": "success", "message": "Security audit completed"}
    
    async def _apply_security_changes(self) -> Dict[str, Any]:
        """Apply security changes"""
        await asyncio.sleep(2)
        return {"status": "success", "message": "Security changes applied"}
    
    async def _verify_security(self) -> Dict[str, Any]:
        """Verify security changes"""
        await asyncio.sleep(1)
        return {"status": "success", "message": "Security changes verified"}
    
    async def request_approval(
        self, 
        workflow_id: str, 
        action: str, 
        user_id: str, 
        description: str
    ) -> Approval:
        """Request approval for a workflow"""
        try:
            approval_id = str(uuid.uuid4())
            
            approval = Approval(
                id=approval_id,
                workflow_id=workflow_id,
                action=action,
                description=description,
                user_id=user_id,
                status=ApprovalStatus.PENDING,
                created_at=datetime.now()
            )
            
            # Store approval
            self.approvals[approval_id] = approval
            
            # Update workflow
            workflow = await self.get_workflow(workflow_id)
            if workflow:
                workflow.status = WorkflowStatus.APPROVAL_REQUIRED
                workflow.approval_id = approval_id
                workflow.updated_at = datetime.now()
            
            logger.info(f"Created approval request {approval_id} for workflow {workflow_id}")
            return approval
            
        except Exception as e:
            logger.error(f"Error requesting approval: {e}")
            raise
    
    async def approve_action(self, approval_id: str, approver_id: str) -> Dict[str, Any]:
        """Approve an action"""
        try:
            approval = self.approvals.get(approval_id)
            if not approval:
                raise ValueError(f"Approval {approval_id} not found")
            
            if approval.status != ApprovalStatus.PENDING:
                raise ValueError(f"Approval {approval_id} is not pending")
            
            # Update approval
            approval.status = ApprovalStatus.APPROVED
            approval.approved_by = approver_id
            approval.approved_at = datetime.now()
            
            # Update workflow
            workflow = await self.get_workflow(approval.workflow_id)
            if workflow:
                workflow.status = WorkflowStatus.PENDING
                workflow.updated_at = datetime.now()
            
            logger.info(f"Approval {approval_id} approved by {approver_id}")
            
            return {
                "approval_id": approval_id,
                "status": "approved",
                "workflow_id": approval.workflow_id
            }
            
        except Exception as e:
            logger.error(f"Error approving action: {e}")
            raise
    
    async def reject_action(self, approval_id: str, rejector_id: str, reason: str = "") -> Dict[str, Any]:
        """Reject an action"""
        try:
            approval = self.approvals.get(approval_id)
            if not approval:
                raise ValueError(f"Approval {approval_id} not found")
            
            if approval.status != ApprovalStatus.PENDING:
                raise ValueError(f"Approval {approval_id} is not pending")
            
            # Update approval
            approval.status = ApprovalStatus.REJECTED
            approval.rejected_by = rejector_id
            approval.rejected_at = datetime.now()
            approval.rejection_reason = reason
            
            # Update workflow
            workflow = await self.get_workflow(approval.workflow_id)
            if workflow:
                workflow.status = WorkflowStatus.CANCELLED
                workflow.updated_at = datetime.now()
            
            logger.info(f"Approval {approval_id} rejected by {rejector_id}")
            
            return {
                "approval_id": approval_id,
                "status": "rejected",
                "workflow_id": approval.workflow_id,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Error rejecting action: {e}")
            raise
    
    async def cancel_workflow(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel a workflow"""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if workflow.user_id != user_id:
                raise ValueError("Only workflow owner can cancel workflow")
            
            if workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                raise ValueError(f"Cannot cancel workflow in {workflow.status} state")
            
            # Update workflow status
            workflow.status = WorkflowStatus.CANCELLED
            workflow.updated_at = datetime.now()
            
            logger.info(f"Workflow {workflow_id} cancelled by {user_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": "cancelled",
                "message": "Workflow cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling workflow: {e}")
            raise
    
    async def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return []
            
            history = []
            
            # Add workflow status changes
            history.append({
                "timestamp": workflow.created_at,
                "event": "workflow_created",
                "details": f"Workflow '{workflow.name}' created"
            })
            
            # Add step executions
            for step in workflow.steps:
                if step.start_time:
                    history.append({
                        "timestamp": step.start_time,
                        "event": "step_started",
                        "details": f"Step {step.step_number}: {step.description}"
                    })
                
                if step.end_time:
                    event = "step_completed" if step.status == "completed" else "step_failed"
                    details = f"Step {step.step_number}: {step.description}"
                    if step.error:
                        details += f" - Error: {step.error}"
                    
                    history.append({
                        "timestamp": step.end_time,
                        "event": event,
                        "details": details
                    })
            
            # Add approval events if applicable
            if workflow.approval_id:
                approval = self.approvals.get(workflow.approval_id)
                if approval:
                    history.append({
                        "timestamp": approval.created_at,
                        "event": "approval_requested",
                        "details": f"Approval requested: {approval.description}"
                    })
                    
                    if approval.approved_at:
                        history.append({
                            "timestamp": approval.approved_at,
                            "event": "approval_granted",
                            "details": f"Approved by {approval.approved_by}"
                        })
                    
                    if approval.rejected_at:
                        history.append({
                            "timestamp": approval.rejected_at,
                            "event": "approval_rejected",
                            "details": f"Rejected by {approval.rejected_by}: {approval.rejection_reason}"
                        })
            
            # Sort by timestamp
            history.sort(key=lambda x: x["timestamp"])
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting workflow history: {e}")
            return [] 