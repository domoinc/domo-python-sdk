"""Async Embed client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.embed import EmbedToken

URL_BASE = "/v1/embed"


class AsyncEmbedClient(AsyncDomoAPIClient):
    """Create embed tokens for Domo cards and dashboards asynchronously.

    Docs: https://developer.domo.com/docs/embed-api-reference/embed
    """

    async def create_card_token(
        self,
        card_id: int,
        expiration: int | None = None,
        **kwargs: Any,
    ) -> EmbedToken:
        """Create an embed token for a card."""
        body: dict[str, Any] = {"cardId": card_id, **kwargs}
        if expiration is not None:
            body["expiration"] = expiration
        data = await self._create(f"{URL_BASE}/card", body)
        return EmbedToken.model_validate(data)

    async def create_dashboard_token(
        self,
        page_id: int,
        expiration: int | None = None,
        **kwargs: Any,
    ) -> EmbedToken:
        """Create an embed token for a dashboard (page)."""
        body: dict[str, Any] = {"pageId": page_id, **kwargs}
        if expiration is not None:
            body["expiration"] = expiration
        data = await self._create(f"{URL_BASE}/dashboard", body)
        return EmbedToken.model_validate(data)
