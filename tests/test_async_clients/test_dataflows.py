"""Tests for AsyncDataflowsClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.dataflows import AsyncDataflowsClient
from domo_sdk.models.dataflows import Dataflow, DataflowExecution
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncDataflowsClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncDataflowsClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncDataflowsCRUD:
    @respx.mock
    async def test_list(self) -> None:
        client, base_url = _make_async_client()
        respx.get(f"{base_url}/v1/dataflows").mock(
            side_effect=[
                Response(
                    200,
                    json=[
                        {"id": 1, "name": "ETL1"},
                        {"id": 2, "name": "ETL2"},
                    ],
                ),
                Response(200, json=[]),
            ]
        )

        result = await client.list()

        assert len(result) == 2
        assert all(isinstance(d, Dataflow) for d in result)
        await client.transport.close()

    @respx.mock
    async def test_get(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/dataflows/1").mock(
            return_value=Response(
                200,
                json={"id": 1, "name": "Sales ETL", "type": "ETL"},
            )
        )

        result = await client.get(1)

        assert route.called
        assert isinstance(result, Dataflow)
        assert result.name == "Sales ETL"
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataflowsExecutions:
    @respx.mock
    async def test_execute(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/dataflows/1/executions"
        ).mock(
            return_value=Response(
                200,
                json={"id": 10, "currentState": "ACTIVE"},
            )
        )

        result = await client.execute(1)

        assert route.called
        assert isinstance(result, DataflowExecution)
        await client.transport.close()

    @respx.mock
    async def test_get_execution(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/v1/dataflows/1/executions/10"
        ).mock(
            return_value=Response(
                200,
                json={"id": 10, "currentState": "SUCCEEDED"},
            )
        )

        result = await client.get_execution(1, 10)

        assert route.called
        assert isinstance(result, DataflowExecution)
        assert result.current_state == "SUCCEEDED"
        await client.transport.close()
