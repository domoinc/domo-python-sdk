"""Alerts client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.alerts import Alert

URL_BASE = "/social/v4/alerts"


class AlertsClient(DomoAPIClient):
    """Manage Domo alerts.

    Docs: https://developer.domo.com/docs/alerts-api-reference/alerts
    """

    def query(self, limit: int = 50, offset: int = 0) -> list[Alert]:
        """Query alerts."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        data = self._list(URL_BASE, params=params)
        return [Alert.model_validate(a) for a in data]

    def get(self, alert_id: int) -> Alert:
        """Retrieve a single alert by ID."""
        data = self._get(f"{URL_BASE}/{alert_id}")
        return Alert.model_validate(data)

    def subscribe(self, alert_id: int) -> None:
        """Subscribe to an alert."""
        self._create(f"{URL_BASE}/{alert_id}/subscribe", None)

    def unsubscribe(self, alert_id: int) -> None:
        """Unsubscribe from an alert."""
        self._delete(f"{URL_BASE}/{alert_id}/subscribe")

    def share(self, alert_id: int, share_data: dict) -> None:
        """Share an alert."""
        self._create(f"{URL_BASE}/{alert_id}/share", share_data)
