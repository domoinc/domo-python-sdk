"""Embed token client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.embed import EmbedToken


class EmbedClient(DomoAPIClient):
    """Generate embed tokens for Domo cards and dashboards.

    Docs: https://developer.domo.com/docs/embed-api-reference/embed
    """

    def create_card_token(
        self, card_id: int, **kwargs: Any
    ) -> EmbedToken:
        """Create an embed token for a card."""
        body = {"cardId": card_id, **kwargs}
        data = self._create("/v1/cards/embed/auth", body)
        return EmbedToken.model_validate(data)

    def create_dashboard_token(
        self, dashboard_id: int, **kwargs: Any
    ) -> EmbedToken:
        """Create an embed token for a dashboard."""
        body = {"dashboardId": dashboard_id, **kwargs}
        data = self._create("/v1/stories/embed/auth", body)
        return EmbedToken.model_validate(data)
