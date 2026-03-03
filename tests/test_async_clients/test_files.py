"""Tests for AsyncFilesClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.files import AsyncFilesClient
from domo_sdk.models.files import File
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncFilesClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncFilesClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncFiles:
    @respx.mock
    async def test_upload(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/files").mock(
            return_value=Response(
                200, json={"id": 1, "name": "data.csv"}
            )
        )

        result = await client.upload(b"hello", "data.csv")

        assert route.called
        assert isinstance(result, File)
        assert result.name == "data.csv"
        await client.transport.close()

    @respx.mock
    async def test_get_details(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/files/1").mock(
            return_value=Response(
                200,
                json={"id": 1, "name": "data.csv", "size": 1024},
            )
        )

        result = await client.get_details("1")

        assert route.called
        assert isinstance(result, File)
        assert result.size == 1024
        await client.transport.close()
