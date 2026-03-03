"""Async Alerts client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.alerts import Alert

URL_BASE = "/v1/alerts"


class AsyncAlertsClient(AsyncDomoAPIClient):
    """Manage Domo alerts asynchronously.

    Docs: https://developer.domo.com/docs/alerts-api-reference/alerts
    """

    async def query(
        self,
        per_page: int = 50,
        offset: int = 0,
    ) -> list[Alert]:
        """List alerts."""
        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        data = await self._list(URL_BASE, params=params)
        return [Alert.model_validate(a) for a in data]

    async def get(self, alert_id: int) -> Alert:
        """Retrieve a single alert by ID."""
        data = await self._get(f"{URL_BASE}/{alert_id}")
        return Alert.model_validate(data)

    async def subscribe(self, alert_id: int, user_id: int) -> None:
        """Subscribe a user to an alert."""
        url = f"{URL_BASE}/{alert_id}/subscribers/{user_id}"
        await self._update(url, None)

    async def unsubscribe(self, alert_id: int, user_id: int) -> None:
        """Unsubscribe a user from an alert."""
        url = f"{URL_BASE}/{alert_id}/subscribers/{user_id}"
        await self._delete(url)

    async def share(self, alert_id: int, user_ids: list[int]) -> None:
        """Share an alert with a list of users."""
        url = f"{URL_BASE}/{alert_id}/share"
        await self._create(url, user_ids)
