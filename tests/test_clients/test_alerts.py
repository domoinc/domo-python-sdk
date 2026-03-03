"""Tests for AlertsClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.alerts import AlertsClient
from domo_sdk.models.alerts import Alert


def _make_client() -> tuple[AlertsClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return AlertsClient(transport), transport


class TestAlertsCRUD:
    def test_query(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "Sales Alert"},
            {"id": 2, "name": "Budget Alert"},
        ]

        result = client.query()

        assert len(result) == 2
        assert all(isinstance(a, Alert) for a in result)
        assert result[0].name == "Sales Alert"

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": 1, "name": "Sales Alert"}

        result = client.get(1)

        assert isinstance(result, Alert)
        assert result.id == 1


class TestAlertsSubscriptions:
    def test_subscribe(self) -> None:
        client, transport = _make_client()
        client.subscribe(1)
        transport.post.assert_called_once()

    def test_unsubscribe(self) -> None:
        client, transport = _make_client()
        client.unsubscribe(1)
        transport.delete.assert_called_once_with(
            "/social/v4/alerts/1/subscribe", params=None
        )

    def test_share(self) -> None:
        client, transport = _make_client()
        client.share(1, {"userIds": [42, 99]})
        transport.post.assert_called_once()
