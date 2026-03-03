"""Tests for RolesClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.roles import RolesClient


def _make_client() -> tuple[RolesClient, MagicMock]:
    """Create a RolesClient with a fully mocked transport."""
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    client = RolesClient(transport)
    return client, transport


class TestRolesClient:
    """Tests for RolesClient operations."""

    def test_list_roles(self) -> None:
        """GET /authorization/v1/roles."""
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "Admin"},
            {"id": 2, "name": "Editor"},
        ]

        result = client.list()

        transport.get.assert_called_once_with(
            "/authorization/v1/roles",
            params=None,
        )
        assert len(result) == 2

    def test_create_role(self) -> None:
        """POST /authorization/v1/roles."""
        client, transport = _make_client()
        transport.post.return_value = {"id": 3, "name": "Viewer"}

        body = {"name": "Viewer", "description": "Read-only access"}
        result = client.create(body)

        transport.post.assert_called_once_with(
            "/authorization/v1/roles",
            body=body,
            params=None,
        )
        assert result["name"] == "Viewer"

    def test_get_role(self) -> None:
        """GET /authorization/v1/roles/{id}."""
        client, transport = _make_client()
        transport.get.return_value = {"id": 1, "name": "Admin"}

        result = client.get(1)

        transport.get.assert_called_once_with(
            "/authorization/v1/roles/1",
            params=None,
        )
        assert result["id"] == 1

    def test_delete_role(self) -> None:
        """DELETE /authorization/v1/roles/{id}."""
        client, transport = _make_client()

        client.delete(1)

        transport.delete.assert_called_once_with("/authorization/v1/roles/1", params=None)

    def test_list_authorities(self) -> None:
        """GET /authorization/v1/roles/{id}/authorities."""
        client, transport = _make_client()
        transport.get.return_value = [
            {"authority": "DATA_MANAGE", "grant_type": "ROLE"},
        ]

        result = client.list_authorities(1)

        transport.get.assert_called_once_with(
            "/authorization/v1/roles/1/authorities",
            params=None,
        )
        assert len(result) == 1
        assert result[0]["authority"] == "DATA_MANAGE"

    def test_update_authorities(self) -> None:
        """PATCH /authorization/v1/roles/{id}/authorities."""
        client, transport = _make_client()
        transport.patch.return_value = {"status": "ok"}

        authorities = [{"authority": "DATA_MANAGE"}, {"authority": "USER_MANAGE"}]
        result = client.update_authorities(1, authorities)

        transport.patch.assert_called_once_with(
            "/authorization/v1/roles/1/authorities",
            body=authorities,
        )
        assert result["status"] == "ok"
