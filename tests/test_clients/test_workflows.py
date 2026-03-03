"""Tests for WorkflowsClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.workflows import WorkflowsClient
from domo_sdk.models.workflows import WorkflowInstance, WorkflowPermission


def _make_client() -> tuple[WorkflowsClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return WorkflowsClient(transport), transport


class TestWorkflowsCRUD:
    def test_start(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": "inst-1",
            "status": "RUNNING",
        }

        result = client.start({"modelId": 1})

        assert isinstance(result, WorkflowInstance)
        assert result.status == "RUNNING"

    def test_get_instance(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": "inst-1",
            "status": "COMPLETED",
        }

        result = client.get_instance("inst-1")

        assert isinstance(result, WorkflowInstance)
        assert result.status == "COMPLETED"

    def test_cancel(self) -> None:
        client, transport = _make_client()
        client.cancel("inst-1")
        transport.post.assert_called_once()


class TestWorkflowsPermissions:
    def test_get_permissions(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"type": "USER", "id": 42, "permissions": ["READ"]},
        ]

        result = client.get_permissions(1)

        assert len(result) == 1
        assert isinstance(result[0], WorkflowPermission)

    def test_set_permissions(self) -> None:
        client, transport = _make_client()
        client.set_permissions(1, [{"type": "USER", "id": 42}])
        transport.post.assert_called_once()
