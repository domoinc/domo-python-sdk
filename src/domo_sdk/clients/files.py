"""Files client for the Domo API."""

from __future__ import annotations

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.files import File

URL_BASE = "/data/v1/data-files"


class FilesClient(DomoAPIClient):
    """Manage Domo data files.

    Docs: https://developer.domo.com/docs/data-files-api-reference/data-files
    """

    def upload(
        self, file_data: bytes, name: str, description: str = ""
    ) -> File:
        """Upload a new file."""
        body = {"name": name, "description": description}
        data = self._create(URL_BASE, body)
        return File.model_validate(data)

    def update(self, file_id: int, file_data: bytes) -> File:
        """Update (replace) an existing file's contents."""
        data = self._upload_csv(f"{URL_BASE}/{file_id}", file_data)
        return File.model_validate(data)

    def get_details(self, file_id: int) -> File:
        """Get file details."""
        data = self._get(
            f"{URL_BASE}/details", params={"fileId": file_id}
        )
        return File.model_validate(data)

    def download(self, file_id: int, revision_id: int) -> bytes:
        """Download a specific file revision.

        Returns raw bytes from the transport layer.
        """
        url = f"{URL_BASE}/{file_id}/revision/{revision_id}"
        return self._get(url)

    def set_permissions(
        self, file_id: int, permissions: list
    ) -> None:
        """Set permissions for a file."""
        self._update(f"{URL_BASE}/{file_id}/permissions", permissions)
