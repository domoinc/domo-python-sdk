"""Tests for AsyncAlertsClient using respx to mock httpx requests."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.alerts import AsyncAlertsClient
from domo_sdk.models.alerts import Alert
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncAlertsClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncAlertsClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncAlertsCRUD:
    @respx.mock
    async def test_query(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/alerts").mock(
            return_value=Response(
                200,
                json=[
                    {"id": 1, "name": "Sales Alert"},
                    {"id": 2, "name": "Budget Alert"},
                ],
            )
        )

        result = await client.query()

        assert route.called
        assert len(result) == 2
        assert all(isinstance(a, Alert) for a in result)
        await client.transport.close()

    @respx.mock
    async def test_get(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/alerts/1").mock(
            return_value=Response(
                200, json={"id": 1, "name": "Sales Alert"}
            )
        )

        result = await client.get(1)

        assert route.called
        assert isinstance(result, Alert)
        assert result.id == 1
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncAlertsSubscriptions:
    @respx.mock
    async def test_subscribe(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(
            f"{base_url}/v1/alerts/1/subscribers/42"
        ).mock(return_value=Response(200, json={}))

        await client.subscribe(1, 42)

        assert route.called
        await client.transport.close()

    @respx.mock
    async def test_unsubscribe(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(
            f"{base_url}/v1/alerts/1/subscribers/42"
        ).mock(return_value=Response(204))

        await client.unsubscribe(1, 42)

        assert route.called
        await client.transport.close()

    @respx.mock
    async def test_share(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/alerts/1/share").mock(
            return_value=Response(200, json={})
        )

        await client.share(1, [42, 99])

        assert route.called
        await client.transport.close()
