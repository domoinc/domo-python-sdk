"""Async Card client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.cards import Card

URL_BASE = "/v1/cards"


class AsyncCardClient(AsyncDomoAPIClient):
    """Manage Domo cards asynchronously.

    Docs: https://developer.domo.com/docs/cards-api-reference/cards
    """

    async def create(self, card_request: dict) -> Card:
        """Create a new card."""
        data = await self._create(URL_BASE, card_request)
        return Card.model_validate(data)

    async def get(self, card_id: int) -> Card:
        """Retrieve a single card by ID."""
        data = await self._get(f"{URL_BASE}/{card_id}")
        return Card.model_validate(data)

    async def list(
        self, per_page: int = 50, offset: int = 0
    ) -> list[Card]:
        """List cards."""
        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        data = await self._list(URL_BASE, params=params)
        return [Card.model_validate(c) for c in data]

    async def update(self, card_id: int, card_update: dict) -> Card:
        """Update an existing card."""
        data = await self._update(f"{URL_BASE}/{card_id}", card_update)
        return Card.model_validate(data)

    async def delete(self, card_id: int) -> None:
        """Delete a card."""
        await self._delete(f"{URL_BASE}/{card_id}")
