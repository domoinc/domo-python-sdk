"""Async Files client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.files import File

URL_BASE = "/v1/files"


class AsyncFilesClient(AsyncDomoAPIClient):
    """Manage Domo file uploads and downloads asynchronously."""

    async def upload(
        self, file_data: bytes, name: str, **kwargs: Any
    ) -> File:
        """Upload a new file."""
        body: dict[str, Any] = {"name": name, **kwargs}
        data = await self._create(URL_BASE, body)
        return File.model_validate(data)

    async def update(self, file_id: str, **kwargs: Any) -> File:
        """Update file metadata."""
        data = await self._update(f"{URL_BASE}/{file_id}", kwargs)
        return File.model_validate(data)

    async def get_details(self, file_id: str) -> File:
        """Get file details."""
        data = await self._get(f"{URL_BASE}/{file_id}")
        return File.model_validate(data)

    async def download(self, file_id: str) -> str:
        """Download file contents.

        Returns the file content as a string (CSV-compatible endpoint).
        """
        url = f"{URL_BASE}/{file_id}/content"
        return await self._download_csv(url, include_header=True)

    async def set_permissions(
        self, file_id: str, permissions: list
    ) -> None:
        """Set permissions for a file."""
        url = f"{URL_BASE}/{file_id}/permissions"
        await self._update(url, permissions)
