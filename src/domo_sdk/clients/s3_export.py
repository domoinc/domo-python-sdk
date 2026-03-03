"""S3 export client for the Domo API."""

from __future__ import annotations

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.s3_export import S3Export

URL_BASE = "/query/v1/export"


class S3ExportClient(DomoAPIClient):
    """Export Domo datasets to S3.

    Docs: https://developer.domo.com/docs/s3-export-api-reference/s3-export
    """

    def start_export(self, dataset_id: str, config: dict) -> S3Export:
        """Start an S3 export for a dataset."""
        data = self._create(f"{URL_BASE}/{dataset_id}", config)
        return S3Export.model_validate(data)

    def get_export_status(self, dataset_id: str) -> S3Export:
        """Get the export status for a dataset."""
        data = self._get(f"{URL_BASE}/{dataset_id}")
        return S3Export.model_validate(data)
