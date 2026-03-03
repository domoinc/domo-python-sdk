"""Async S3 Export client for the Domo API."""

from __future__ import annotations

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.s3_export import S3Export

URL_BASE = "/v1/datasets"


class AsyncS3ExportClient(AsyncDomoAPIClient):
    """Manage Domo dataset S3 exports asynchronously."""

    async def start_export(
        self,
        dataset_id: str,
        export_config: dict | None = None,
    ) -> S3Export:
        """Start an S3 export for a dataset."""
        url = f"{URL_BASE}/{dataset_id}/exports"
        data = await self._create(url, export_config or {})
        return S3Export.model_validate(data)

    async def get_export_status(
        self, dataset_id: str, export_id: str
    ) -> S3Export:
        """Get the status of an S3 export."""
        url = f"{URL_BASE}/{dataset_id}/exports/{export_id}"
        data = await self._get(url)
        return S3Export.model_validate(data)
