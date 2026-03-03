"""Async Activity Log client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.activity_log import AuditEntry

URL_BASE = "/v1/audit"


class AsyncActivityLogClient(AsyncDomoAPIClient):
    """Query the Domo activity log asynchronously.

    Docs: https://developer.domo.com/docs/activity-log-api-reference/activity-log
    """

    async def query(
        self,
        start: int = 0,
        end: int = 0,
        limit: int = 50,
        offset: int = 0,
        user: int | None = None,
    ) -> list[AuditEntry]:
        """Query activity log entries."""
        params: dict[str, Any] = {
            "start": start,
            "end": end,
            "limit": limit,
            "offset": offset,
        }
        if user is not None:
            params["user"] = user

        data = await self._list(URL_BASE, params=params)
        return [AuditEntry.model_validate(e) for e in data]
