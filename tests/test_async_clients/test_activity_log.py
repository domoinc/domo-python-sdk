"""Tests for AsyncActivityLogClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.activity_log import AsyncActivityLogClient
from domo_sdk.models.activity_log import AuditEntry
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncActivityLogClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncActivityLogClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncActivityLog:
    @respx.mock
    async def test_query(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/audit").mock(
            return_value=Response(
                200,
                json=[
                    {"userName": "admin", "actionType": "LOGIN"},
                    {"userName": "user1", "actionType": "VIEWED"},
                ],
            )
        )

        result = await client.query()

        assert route.called
        assert len(result) == 2
        assert all(isinstance(e, AuditEntry) for e in result)
        await client.transport.close()
