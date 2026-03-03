"""Tests for RolesClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.roles import RolesClient
from domo_sdk.models.roles import Authority, Role


def _make_client() -> tuple[RolesClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return RolesClient(transport), transport


class TestRolesCRUD:
    def test_list(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "Admin"},
            {"id": 2, "name": "Privileged"},
        ]

        result = client.list()

        assert len(result) == 2
        assert all(isinstance(r, Role) for r in result)
        assert result[0].name == "Admin"

    def test_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"id": 3, "name": "Custom"}

        result = client.create({"name": "Custom"})

        assert isinstance(result, Role)
        assert result.name == "Custom"

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": 1, "name": "Admin"}

        result = client.get(1)

        assert isinstance(result, Role)
        assert result.id == 1

    def test_delete(self) -> None:
        client, transport = _make_client()
        client.delete(1)
        transport.delete.assert_called_once_with(
            "/authorization/v1/roles/1", params=None
        )


class TestRolesAuthorities:
    def test_list_authorities(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "authority": "DATA"},
            {"id": 2, "authority": "USER"},
        ]

        result = client.list_authorities(1)

        assert len(result) == 2
        assert all(isinstance(a, Authority) for a in result)

    def test_update_authorities(self) -> None:
        client, transport = _make_client()
        transport.patch.return_value = [
            {"id": 1, "authority": "DATA"},
        ]

        result = client.update_authorities(1, [{"authority": "DATA"}])

        assert len(result) == 1
        assert isinstance(result[0], Authority)
