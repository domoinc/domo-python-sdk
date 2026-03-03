"""Async Page client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.pages import Page, PageCollection

URL_BASE = "/v1/pages"


class AsyncPageClient(AsyncDomoAPIClient):
    """Manage Domo pages asynchronously.

    Docs: https://developer.domo.com/docs/page-api-reference/page
    """

    async def create(self, name: str, **kwargs: Any) -> Page:
        """Create a new page."""
        body: dict[str, Any] = {"name": name, **kwargs}
        data = await self._create(URL_BASE, body)
        return Page.model_validate(data)

    async def get(self, page_id: int) -> Page:
        """Retrieve a single page by ID."""
        data = await self._get(f"{URL_BASE}/{page_id}")
        return Page.model_validate(data)

    async def list(self) -> list[Page]:
        """List all pages."""
        data = await self._list(URL_BASE)
        return [Page.model_validate(p) for p in data]

    async def update(self, page_id: int, **kwargs: Any) -> Page:
        """Update an existing page."""
        data = await self._update(f"{URL_BASE}/{page_id}", kwargs)
        return Page.model_validate(data)

    async def delete(self, page_id: int) -> None:
        """Delete a page."""
        await self._delete(f"{URL_BASE}/{page_id}")

    # ------------------------------------------------------------------
    # Collections
    # ------------------------------------------------------------------

    async def get_collections(
        self, page_id: int
    ) -> list[PageCollection]:
        """List collections on a page."""
        url = f"{URL_BASE}/{page_id}/collections"
        data = await self._list(url)
        return [PageCollection.model_validate(c) for c in data]

    async def create_collection(
        self, page_id: int, title: str, **kwargs: Any
    ) -> PageCollection:
        """Create a new collection on a page."""
        url = f"{URL_BASE}/{page_id}/collections"
        body: dict[str, Any] = {"title": title, **kwargs}
        data = await self._create(url, body)
        return PageCollection.model_validate(data)

    async def update_collection(
        self, page_id: int, collection_id: int, **kwargs: Any
    ) -> PageCollection:
        """Update a collection on a page."""
        url = f"{URL_BASE}/{page_id}/collections/{collection_id}"
        data = await self._update(url, kwargs)
        return PageCollection.model_validate(data)

    async def delete_collection(
        self, page_id: int, collection_id: int
    ) -> None:
        """Delete a collection from a page."""
        url = f"{URL_BASE}/{page_id}/collections/{collection_id}"
        await self._delete(url)
