"""Comment schemas export."""
from app.schemas.auditlog import (
    CommentBase,
    CommentCreate,
    CommentRead,
)

CommentUpdate = CommentCreate

__all__ = [
    "CommentBase",
    "CommentCreate",
    "CommentUpdate",
    "CommentRead",
]
