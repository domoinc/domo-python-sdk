"""Tests for FilesClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.files import FilesClient
from domo_sdk.models.files import File


def _make_client() -> tuple[FilesClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return FilesClient(transport), transport


class TestFilesCRUD:
    def test_upload(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 1,
            "name": "data.csv",
        }

        result = client.upload(b"hello", "data.csv")

        assert isinstance(result, File)
        assert result.name == "data.csv"

    def test_get_details(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 1,
            "name": "data.csv",
            "size": 1024,
        }

        result = client.get_details(1)

        assert isinstance(result, File)
        assert result.size == 1024

    def test_set_permissions(self) -> None:
        client, transport = _make_client()
        client.set_permissions(1, [{"userId": 42}])
        transport.put.assert_called_once()
