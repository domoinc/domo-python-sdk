"""Tests for S3ExportClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.s3_export import S3ExportClient
from domo_sdk.models.s3_export import S3Export


def _make_client() -> tuple[S3ExportClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return S3ExportClient(transport), transport


class TestS3Export:
    def test_start_export(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "exportId": "exp-1",
            "datasetId": "ds-1",
            "status": "STARTED",
        }

        result = client.start_export("ds-1", {"bucket": "my-bucket"})

        assert isinstance(result, S3Export)
        assert result.status == "STARTED"

    def test_get_export_status(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "exportId": "exp-1",
            "datasetId": "ds-1",
            "status": "COMPLETED",
        }

        result = client.get_export_status("ds-1")

        assert isinstance(result, S3Export)
        assert result.status == "COMPLETED"
