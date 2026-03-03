"""Tests for UserClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.users import UserClient
from domo_sdk.models.users import User


def _make_client() -> tuple[UserClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return UserClient(transport), transport


class TestUserCRUD:
    def test_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 1,
            "name": "Alice",
            "email": "alice@co.com",
            "role": "Admin",
        }

        result = client.create(
            {"name": "Alice", "email": "alice@co.com", "role": "Admin"}
        )

        assert isinstance(result, User)
        assert result.name == "Alice"

    def test_create_with_invite(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"id": 1, "name": "Bob"}

        client.create({"name": "Bob"}, send_invite=True)

        transport.post.assert_called_once_with(
            "/v1/users",
            body={"name": "Bob"},
            params={"sendInvite": True},
        )

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": 42, "name": "Alice"}

        result = client.get(42)

        assert isinstance(result, User)
        assert result.id == 42

    def test_list_pagination(self) -> None:
        client, transport = _make_client()
        transport.get.side_effect = [
            [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
            [],
        ]

        results = list(client.list(per_page=2))

        assert len(results) == 2
        assert all(isinstance(u, User) for u in results)

    def test_update(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {"id": 1, "name": "Updated"}

        result = client.update(1, {"name": "Updated"})

        assert isinstance(result, User)
        assert result.name == "Updated"

    def test_delete(self) -> None:
        client, transport = _make_client()
        client.delete(1)
        transport.delete.assert_called_once_with(
            "/v1/users/1", params=None
        )
