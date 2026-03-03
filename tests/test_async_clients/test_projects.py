"""Tests for AsyncProjectsClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.projects import AsyncProjectsClient
from domo_sdk.models.projects import Project, Task, TaskList
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncProjectsClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncProjectsClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncProjectsCRUD:
    @respx.mock
    async def test_create_project(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/projects").mock(
            return_value=Response(
                200, json={"id": 1, "name": "Alpha"}
            )
        )

        result = await client.create_project({"name": "Alpha"})

        assert route.called
        assert isinstance(result, Project)
        assert result.name == "Alpha"
        await client.transport.close()

    @respx.mock
    async def test_list_projects(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/projects").mock(
            return_value=Response(
                200,
                json=[
                    {"id": 1, "name": "A"},
                    {"id": 2, "name": "B"},
                ],
            )
        )

        result = await client.list_projects()

        assert route.called
        assert len(result) == 2
        assert all(isinstance(p, Project) for p in result)
        await client.transport.close()

    @respx.mock
    async def test_delete_project(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/v1/projects/1").mock(
            return_value=Response(204)
        )

        await client.delete_project(1)

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncProjectsTasks:
    @respx.mock
    async def test_create_task(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/projects/1/lists/10/tasks"
        ).mock(
            return_value=Response(
                200,
                json={"id": 100, "taskName": "Fix bug"},
            )
        )

        result = await client.create_task(
            1, 10, {"taskName": "Fix bug"}
        )

        assert route.called
        assert isinstance(result, Task)
        assert result.task_name == "Fix bug"
        await client.transport.close()

    @respx.mock
    async def test_create_list(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/projects/1/lists"
        ).mock(
            return_value=Response(
                200,
                json={"id": 10, "name": "Backlog"},
            )
        )

        result = await client.create_list(
            1, {"name": "Backlog"}
        )

        assert route.called
        assert isinstance(result, TaskList)
        await client.transport.close()
