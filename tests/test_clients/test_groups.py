"""Tests for GroupClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.groups import GroupClient
from domo_sdk.models.groups import Group


def _make_client() -> tuple[GroupClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return GroupClient(transport), transport


class TestGroupCRUD:
    def test_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"id": 1, "name": "Admins"}

        result = client.create({"name": "Admins"})

        assert isinstance(result, Group)
        assert result.name == "Admins"

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": 1, "name": "Sales"}

        result = client.get(1)

        assert isinstance(result, Group)
        assert result.id == 1

    def test_list(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
        ]

        result = client.list()

        assert len(result) == 2
        assert all(isinstance(g, Group) for g in result)

    def test_update(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {"id": 1, "name": "Updated"}

        result = client.update(1, {"name": "Updated"})

        assert isinstance(result, Group)
        assert result.name == "Updated"

    def test_delete(self) -> None:
        client, transport = _make_client()
        client.delete(1)
        transport.delete.assert_called_once_with(
            "/v1/groups/1", params=None
        )


class TestGroupUsers:
    def test_add_user(self) -> None:
        client, transport = _make_client()
        client.add_user(1, 42)
        transport.put.assert_called_once()

    def test_remove_user(self) -> None:
        client, transport = _make_client()
        client.remove_user(1, 42)
        transport.delete.assert_called_once_with(
            "/v1/groups/1/users/42", params=None
        )

    def test_list_users(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [42, 99, 101]

        result = client.list_users(1)

        assert result == [42, 99, 101]
