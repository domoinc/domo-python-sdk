"""Tests for AsyncConnectorsClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.connectors import AsyncConnectorsClient
from domo_sdk.models.streams import StreamExecution
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncConnectorsClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncConnectorsClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncConnectors:
    @respx.mock
    async def test_run(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/streams/1/executions"
        ).mock(
            return_value=Response(
                200,
                json={"id": 100, "currentState": "ACTIVE"},
            )
        )

        result = await client.run(1)

        assert route.called
        assert isinstance(result, StreamExecution)
        assert result.current_state == "ACTIVE"
        await client.transport.close()
