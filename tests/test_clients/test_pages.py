"""Tests for PageClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.pages import PageClient
from domo_sdk.models.pages import Page, PageCollection


def _make_client() -> tuple[PageClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return PageClient(transport), transport


class TestPageCRUD:
    def test_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"id": 1, "name": "Dashboard"}

        result = client.create("Dashboard")

        assert isinstance(result, Page)
        assert result.name == "Dashboard"

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": 1, "name": "Sales"}

        result = client.get(1)

        assert isinstance(result, Page)
        assert result.id == 1

    def test_list(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
        ]

        result = client.list()

        assert len(result) == 2
        assert all(isinstance(p, Page) for p in result)

    def test_update(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {"id": 1, "name": "Updated"}

        result = client.update(1, name="Updated")

        assert isinstance(result, Page)
        assert result.name == "Updated"

    def test_delete(self) -> None:
        client, transport = _make_client()
        client.delete(1)
        transport.delete.assert_called_once_with(
            "/v1/pages/1", params=None
        )


class TestPageCollections:
    def test_get_collections(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 10, "title": "KPIs"},
            {"id": 11, "title": "Charts"},
        ]

        result = client.get_collections(1)

        assert len(result) == 2
        assert all(isinstance(c, PageCollection) for c in result)
        assert result[0].title == "KPIs"

    def test_create_collection(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"id": 10, "title": "New"}

        result = client.create_collection(1, "New")

        assert isinstance(result, PageCollection)
        assert result.title == "New"

    def test_update_collection(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {"id": 10, "title": "Updated"}

        result = client.update_collection(1, 10, title="Updated")

        assert isinstance(result, PageCollection)

    def test_delete_collection(self) -> None:
        client, transport = _make_client()
        client.delete_collection(1, 10)
        transport.delete.assert_called_once_with(
            "/v1/pages/1/collections/10", params=None
        )
