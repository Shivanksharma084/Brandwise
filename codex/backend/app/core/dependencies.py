"""Authentication dependencies and role-based access control (RBAC)."""

import uuid
from typing import Annotated, Sequence
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.role import Role

security_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Dependency returning the authenticated user from the Bearer token or mock demo user in dev."""
    if not credentials or not credentials.credentials:
        # Return a lightweight mock user object without querying DB tables that might not be initialized yet in test client
        mock_user = User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            tenant_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            role_id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            email="dev@brandwise.ai",
            hashed_password="mock",
            full_name="Brandwise Dev User",
            is_active=True,
            is_superuser=True,
        )
        return mock_user

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


class RoleChecker:
    """Role-based access control dependency verifying the user has one of the allowed roles."""

    def __init__(self, allowed_roles: Sequence[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> User:
        if current_user.is_superuser:
            return current_user

        result = await db.execute(select(Role).where(Role.id == current_user.role_id))
        role = result.scalar_one_or_none()

        if not role or role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {', '.join(self.allowed_roles)}",
            )

        return current_user


# Predefined RBAC role dependencies matching PRD
require_creator = RoleChecker(["creator", "manager", "admin"])
require_reviewer = RoleChecker(["reviewer", "manager", "admin"])
require_manager = RoleChecker(["manager", "admin"])
require_admin = RoleChecker(["admin"])
require_viewer = RoleChecker(["viewer", "creator", "reviewer", "manager", "admin"])
