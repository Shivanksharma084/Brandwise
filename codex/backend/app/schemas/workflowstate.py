"""WorkflowState schemas export."""
from app.schemas.auditlog import (
    WorkflowStateBase,
    WorkflowStateCreate,
    WorkflowStateRead,
)

WorkflowStateUpdate = WorkflowStateCreate  # alias for completeness

__all__ = [
    "WorkflowStateBase",
    "WorkflowStateCreate",
    "WorkflowStateUpdate",
    "WorkflowStateRead",
]
