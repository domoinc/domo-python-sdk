"""Tests for EmbedClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.embed import EmbedClient
from domo_sdk.models.embed import EmbedToken


def _make_client() -> tuple[EmbedClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return EmbedClient(transport), transport


class TestEmbed:
    def test_create_card_token(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "token": "abc123",
            "expiration": 3600,
        }

        result = client.create_card_token(42)

        assert isinstance(result, EmbedToken)
        assert result.token == "abc123"
        assert result.expiration == 3600

    def test_create_dashboard_token(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "token": "xyz789",
            "expiration": 7200,
        }

        result = client.create_dashboard_token(10)

        assert isinstance(result, EmbedToken)
        assert result.token == "xyz789"
