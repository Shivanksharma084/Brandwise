"""Tenant isolation middleware and context handling."""

import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.core.database import async_session_factory


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware extracting tenant context from request headers/host and setting it on the DB session."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract tenant from header 'X-Tenant-ID' or subdomains
        tenant_id_str = request.headers.get("X-Tenant-ID")

        if tenant_id_str:
            try:
                request.state.tenant_id = uuid.UUID(tenant_id_str)
            except ValueError:
                request.state.tenant_id = None
        else:
            request.state.tenant_id = None

        response = await call_next(request)
        return response
