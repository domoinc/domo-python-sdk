"""Page client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.pages import Page, PageCollection

URL_BASE = "/v1/pages"


class PageClient(DomoAPIClient):
    """Manage Domo pages.

    Docs: https://developer.domo.com/docs/page-api-reference/page
    """

    def create(self, name: str, **kwargs: Any) -> Page:
        """Create a new page."""
        body = {"name": name, **kwargs}
        data = self._create(URL_BASE, body)
        return Page.model_validate(data)

    def get(self, page_id: int) -> Page:
        """Retrieve a single page by ID."""
        data = self._get(f"{URL_BASE}/{page_id}")
        return Page.model_validate(data)

    def list(self) -> list[Page]:
        """List all pages."""
        data = self._list(URL_BASE)
        return [Page.model_validate(p) for p in data]

    def update(self, page_id: int, **kwargs: Any) -> Page:
        """Update an existing page."""
        data = self._update(f"{URL_BASE}/{page_id}", kwargs)
        return Page.model_validate(data)

    def delete(self, page_id: int) -> None:
        """Delete a page."""
        self._delete(f"{URL_BASE}/{page_id}")

    def get_collections(
        self, page_id: int
    ) -> list[PageCollection]:
        """List collections on a page."""
        data = self._list(f"{URL_BASE}/{page_id}/collections")
        return [PageCollection.model_validate(c) for c in data]

    def create_collection(
        self, page_id: int, title: str, **kwargs: Any
    ) -> PageCollection:
        """Create a collection on a page."""
        body = {"title": title, **kwargs}
        data = self._create(
            f"{URL_BASE}/{page_id}/collections", body
        )
        return PageCollection.model_validate(data)

    def update_collection(
        self, page_id: int, collection_id: int, **kwargs: Any
    ) -> PageCollection:
        """Update a collection on a page."""
        data = self._update(
            f"{URL_BASE}/{page_id}/collections/{collection_id}", kwargs
        )
        return PageCollection.model_validate(data)

    def delete_collection(
        self, page_id: int, collection_id: int
    ) -> None:
        """Delete a collection from a page."""
        self._delete(
            f"{URL_BASE}/{page_id}/collections/{collection_id}"
        )
