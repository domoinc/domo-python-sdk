"""Tests for AsyncEmbedClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.embed import AsyncEmbedClient
from domo_sdk.models.embed import EmbedToken
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncEmbedClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncEmbedClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncEmbed:
    @respx.mock
    async def test_create_card_token(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/embed/card").mock(
            return_value=Response(
                200,
                json={"token": "abc123", "expiration": 3600},
            )
        )

        result = await client.create_card_token(42)

        assert route.called
        assert isinstance(result, EmbedToken)
        assert result.token == "abc123"
        await client.transport.close()

    @respx.mock
    async def test_create_dashboard_token(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/embed/dashboard").mock(
            return_value=Response(
                200,
                json={"token": "xyz789", "expiration": 7200},
            )
        )

        result = await client.create_dashboard_token(10)

        assert route.called
        assert isinstance(result, EmbedToken)
        assert result.token == "xyz789"
        await client.transport.close()
