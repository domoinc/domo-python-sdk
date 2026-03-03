"""Tests for AccountClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.accounts import AccountClient
from domo_sdk.models.accounts import Account


def _make_client() -> tuple[AccountClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return AccountClient(transport), transport


class TestAccountCRUD:
    def test_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"id": "1", "name": "Snowflake"}

        result = client.create(name="Snowflake")

        assert isinstance(result, Account)
        assert result.name == "Snowflake"

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": "1", "name": "Snowflake"}

        result = client.get("1")

        assert isinstance(result, Account)
        assert result.id == "1"

    def test_list_single_page(self) -> None:
        client, transport = _make_client()
        transport.get.side_effect = [
            [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}],
            [],
        ]

        result = list(client.list())

        assert len(result) == 2
        assert all(isinstance(a, Account) for a in result)

    def test_list_with_limit(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": "1", "name": "A"},
            {"id": "2", "name": "B"},
        ]

        result = list(client.list(limit=1))

        assert len(result) == 1
        assert isinstance(result[0], Account)

    def test_list_invalid_per_page(self) -> None:
        client, _ = _make_client()
        import pytest

        with pytest.raises(ValueError, match="per_page must be between"):
            list(client.list(per_page=0))

    def test_update(self) -> None:
        client, transport = _make_client()
        transport.patch.return_value = {
            "id": "1",
            "name": "Updated",
        }

        result = client.update("1", name="Updated")

        assert isinstance(result, Account)
        assert result.name == "Updated"

    def test_delete(self) -> None:
        client, transport = _make_client()
        client.delete("1")
        transport.delete.assert_called_once_with(
            "/v1/accounts/1", params=None
        )
