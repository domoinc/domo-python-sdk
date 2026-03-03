"""Activity log (audit) client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.activity_log import AuditEntry

URL_BASE = "/v1/audit"


class ActivityLogClient(DomoAPIClient):
    """Query the Domo activity log (audit trail).

    Docs: https://developer.domo.com/docs/activity-log-api-reference/activity-log
    """

    def query(
        self,
        user: int | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditEntry]:
        """Query audit log entries."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if user is not None:
            params["user"] = user
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        data = self._list(URL_BASE, params=params)
        return [AuditEntry.model_validate(e) for e in data]
