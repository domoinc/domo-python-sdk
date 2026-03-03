"""Tests for AsyncWorkflowsClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.workflows import AsyncWorkflowsClient
from domo_sdk.models.workflows import WorkflowInstance, WorkflowPermission
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncWorkflowsClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncWorkflowsClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncWorkflowsCRUD:
    @respx.mock
    async def test_start(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/workflows/1/start"
        ).mock(
            return_value=Response(
                200,
                json={"id": "inst-1", "status": "RUNNING"},
            )
        )

        result = await client.start(1, {"param": "value"})

        assert route.called
        assert isinstance(result, WorkflowInstance)
        assert result.status == "RUNNING"
        await client.transport.close()

    @respx.mock
    async def test_get_instance(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/v1/workflows/1/instances/100"
        ).mock(
            return_value=Response(
                200,
                json={"id": "inst-1", "status": "COMPLETED"},
            )
        )

        result = await client.get_instance(1, 100)

        assert route.called
        assert isinstance(result, WorkflowInstance)
        assert result.status == "COMPLETED"
        await client.transport.close()

    @respx.mock
    async def test_cancel(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/workflows/1/instances/100/cancel"
        ).mock(return_value=Response(200, json={}))

        await client.cancel(1, 100)

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncWorkflowsPermissions:
    @respx.mock
    async def test_get_permissions(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/v1/workflows/1/permissions"
        ).mock(
            return_value=Response(
                200,
                json=[
                    {
                        "type": "USER",
                        "id": 42,
                        "permissions": ["READ"],
                    }
                ],
            )
        )

        result = await client.get_permissions(1)

        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], WorkflowPermission)
        await client.transport.close()
