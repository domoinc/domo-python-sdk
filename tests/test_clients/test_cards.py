"""Tests for CardClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.cards import CardClient
from domo_sdk.models.cards import Card


def _make_client() -> tuple[CardClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return CardClient(transport), transport


class TestCardCRUD:
    def test_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"id": 1, "title": "Sales Card"}

        result = client.create({"title": "Sales Card"})

        assert isinstance(result, Card)
        assert result.name == "Sales Card"

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": 1, "title": "Sales Card"}

        result = client.get(1)

        assert isinstance(result, Card)
        assert result.id == 1

    def test_list(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "title": "A"},
            {"id": 2, "title": "B"},
        ]

        result = client.list()

        assert len(result) == 2
        assert all(isinstance(c, Card) for c in result)

    def test_update(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {"id": 1, "title": "Updated"}

        result = client.update(1, {"title": "Updated"})

        assert isinstance(result, Card)
        assert result.name == "Updated"

    def test_delete(self) -> None:
        client, transport = _make_client()
        client.delete(1)
        transport.delete.assert_called_once_with(
            "/v1/cards/1", params=None
        )
