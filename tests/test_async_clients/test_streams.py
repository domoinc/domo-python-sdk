"""Tests for AsyncStreamClient using respx to mock httpx requests."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.streams import AsyncStreamClient
from domo_sdk.models.streams import Stream, StreamExecution
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncStreamClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncStreamClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncStreamCRUD:
    """Async stream CRUD tests."""

    @respx.mock
    async def test_create(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/streams").mock(
            return_value=Response(
                200,
                json={"id": 1, "updateMethod": "REPLACE"},
            )
        )

        result = await client.create({"updateMethod": "REPLACE"})

        assert route.called
        assert isinstance(result, Stream)
        assert result.id == 1
        await client.transport.close()

    @respx.mock
    async def test_get(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/streams/42").mock(
            return_value=Response(
                200, json={"id": 42, "updateMethod": "APPEND"}
            )
        )

        result = await client.get(42)

        assert route.called
        assert isinstance(result, Stream)
        assert result.id == 42
        await client.transport.close()

    @respx.mock
    async def test_search(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/streams/search").mock(
            return_value=Response(200, json=[{"id": 1}, {"id": 2}])
        )

        results = await client.search("sales")

        assert route.called
        assert len(results) == 2
        assert all(isinstance(s, Stream) for s in results)
        await client.transport.close()

    @respx.mock
    async def test_delete(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/v1/streams/1").mock(
            return_value=Response(204)
        )

        await client.delete(1)

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncStreamExecutions:
    """Async execution tests."""

    @respx.mock
    async def test_create_execution(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/streams/1/executions"
        ).mock(
            return_value=Response(
                200,
                json={"id": 100, "currentState": "ACTIVE"},
            )
        )

        result = await client.create_execution(1)

        assert route.called
        assert isinstance(result, StreamExecution)
        assert result.id == 100
        await client.transport.close()

    @respx.mock
    async def test_get_execution(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/v1/streams/1/executions/100"
        ).mock(
            return_value=Response(
                200,
                json={"id": 100, "currentState": "ACTIVE", "rows": 500},
            )
        )

        result = await client.get_execution(1, 100)

        assert route.called
        assert isinstance(result, StreamExecution)
        assert result.rows == 500
        await client.transport.close()

    @respx.mock
    async def test_list_executions(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/v1/streams/1/executions"
        ).mock(
            return_value=Response(
                200,
                json=[
                    {"id": 100, "currentState": "ACTIVE"},
                    {"id": 101, "currentState": "SUCCEEDED"},
                ],
            )
        )

        results = await client.list_executions(1)

        assert route.called
        assert len(results) == 2
        assert all(isinstance(e, StreamExecution) for e in results)
        await client.transport.close()

    @respx.mock
    async def test_commit_execution(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(
            f"{base_url}/v1/streams/1/executions/100/commit"
        ).mock(
            return_value=Response(
                200,
                json={"id": 100, "currentState": "SUCCEEDED"},
            )
        )

        result = await client.commit_execution(1, 100)

        assert route.called
        assert isinstance(result, StreamExecution)
        assert result.current_state == "SUCCEEDED"
        await client.transport.close()

    @respx.mock
    async def test_abort_execution(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(
            f"{base_url}/v1/streams/1/executions/100/abort"
        ).mock(return_value=Response(200, json={}))

        await client.abort_execution(1, 100)

        assert route.called
        await client.transport.close()
