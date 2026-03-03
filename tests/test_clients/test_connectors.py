"""Tests for ConnectorsClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.connectors import ConnectorsClient
from domo_sdk.models.streams import StreamExecution


def _make_client() -> tuple[ConnectorsClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return ConnectorsClient(transport), transport


class TestConnectors:
    def test_run(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 100,
            "currentState": "ACTIVE",
        }

        result = client.run(1)

        assert isinstance(result, StreamExecution)
        assert result.id == 100
        assert result.current_state == "ACTIVE"
