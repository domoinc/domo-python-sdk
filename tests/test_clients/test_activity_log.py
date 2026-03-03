"""Tests for ActivityLogClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.activity_log import ActivityLogClient
from domo_sdk.models.activity_log import AuditEntry


def _make_client() -> tuple[ActivityLogClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return ActivityLogClient(transport), transport


class TestActivityLog:
    def test_query(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"userName": "admin", "actionType": "LOGIN"},
            {"userName": "user1", "actionType": "VIEWED"},
        ]

        result = client.query()

        assert len(result) == 2
        assert all(isinstance(e, AuditEntry) for e in result)
        assert result[0].user_name == "admin"

    def test_query_with_filters(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"userName": "admin", "actionType": "LOGIN"},
        ]

        result = client.query(user=42, start=1000, end=2000)

        assert len(result) == 1
        assert isinstance(result[0], AuditEntry)
