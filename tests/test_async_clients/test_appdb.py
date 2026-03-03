"""Tests for AsyncAppDBClient using respx to mock httpx requests."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.appdb import AsyncAppDBClient
from domo_sdk.models.appdb import (
    AppDBCollection,
    AppDBDocument,
    BulkOperationResult,
)
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import DeveloperTokenCredentials, DeveloperTokenStrategy


def _make_async_client() -> tuple[AsyncAppDBClient, str]:
    """Create an AsyncAppDBClient backed by a real AsyncTransport."""
    creds = DeveloperTokenCredentials(token="test-token", instance_domain="test.domo.com")
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncAppDBClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncCollectionOperations:
    """Async collection CRUD tests."""

    @respx.mock
    async def test_create_collection(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/datastores/v1/collections").mock(
            return_value=Response(200, json={"id": "col-1", "name": "test", "datastoreId": "ds-1"})
        )

        result = await client.create_collection("test")

        assert route.called
        assert isinstance(result, AppDBCollection)
        assert result.name == "test"
        await client.transport.close()

    @respx.mock
    async def test_get_collection(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/datastores/v1/collections/col-1").mock(
            return_value=Response(200, json={"id": "col-1", "name": "my-col", "datastoreId": "ds-1"})
        )

        result = await client.get_collection("col-1")

        assert route.called
        assert isinstance(result, AppDBCollection)
        assert result.id == "col-1"
        await client.transport.close()

    @respx.mock
    async def test_list_collections(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/datastores/v1/collections").mock(
            return_value=Response(200, json=[
                {"id": "col-1", "name": "first"},
                {"id": "col-2", "name": "second"},
            ])
        )

        result = await client.list_collections()

        assert route.called
        assert len(result) == 2
        assert all(isinstance(c, AppDBCollection) for c in result)
        await client.transport.close()

    @respx.mock
    async def test_delete_collection(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/datastores/v1/collections/col-1").mock(
            return_value=Response(204)
        )

        await client.delete_collection("col-1")

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDocumentOperations:
    """Async document CRUD tests."""

    @respx.mock
    async def test_create_document(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/datastores/v1/collections/col-1/documents").mock(
            return_value=Response(200, json={
                "id": "doc-1", "content": {"title": "Hello"},
                "datastoreId": "ds-1", "collectionId": "col-1", "owner": 123,
            })
        )

        result = await client.create_document("col-1", {"title": "Hello"})

        assert route.called
        assert isinstance(result, AppDBDocument)
        assert result.content["title"] == "Hello"
        await client.transport.close()

    @respx.mock
    async def test_get_document(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/datastores/v1/collections/col-1/documents/doc-1").mock(
            return_value=Response(200, json={
                "id": "doc-1", "content": {"key": "value"},
                "datastoreId": "ds-1", "collectionId": "col-1",
            })
        )

        result = await client.get_document("col-1", "doc-1")

        assert route.called
        assert isinstance(result, AppDBDocument)
        assert result.id == "doc-1"
        await client.transport.close()

    @respx.mock
    async def test_list_documents(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/datastores/v1/collections/col-1/documents").mock(
            return_value=Response(200, json=[
                {"id": "doc-1", "content": {"a": 1}},
                {"id": "doc-2", "content": {"b": 2}},
            ])
        )

        result = await client.list_documents("col-1")

        assert route.called
        assert len(result) == 2
        assert all(isinstance(d, AppDBDocument) for d in result)
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncQueryOperations:
    """Async query tests."""

    @respx.mock
    async def test_query_basic(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/datastores/v2/collections/col-1/documents/query").mock(
            return_value=Response(200, json=[
                {"id": "doc-1", "content": {"status": "active"}},
            ])
        )

        result = await client.query("col-1", {"content.status": {"$eq": "active"}})

        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], AppDBDocument)
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncBulkOperations:
    """Async bulk operation tests."""

    @respx.mock
    async def test_bulk_create(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/datastores/v1/collections/col-1/documents/bulk").mock(
            return_value=Response(200, json={"Created": 2, "Updated": 0, "Deleted": 0})
        )

        result = await client.bulk_create("col-1", [{"a": 1}, {"b": 2}])

        assert route.called
        assert isinstance(result, BulkOperationResult)
        assert result.created == 2
        await client.transport.close()

    @respx.mock
    async def test_bulk_delete(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/datastores/v1/collections/col-1/documents/bulk").mock(
            return_value=Response(200, json={"Deleted": 3})
        )

        result = await client.bulk_delete("col-1", ["id-1", "id-2", "id-3"])

        assert route.called
        assert isinstance(result, BulkOperationResult)
        assert result.deleted == 3
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncPermissions:
    """Async permission tests."""

    @respx.mock
    async def test_set_permission(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(f"{base_url}/datastores/v1/collections/col-1/permission/USER/123").mock(
            return_value=Response(204)
        )

        await client.set_permission("col-1", "USER", "123", ["read", "write"])

        assert route.called
        await client.transport.close()

    @respx.mock
    async def test_remove_permission(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/datastores/v1/collections/col-1/permission/GROUP/456").mock(
            return_value=Response(204)
        )

        await client.remove_permission("col-1", "GROUP", "456")

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncExport:
    """Async export tests."""

    @respx.mock
    async def test_export(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/datastores/v1/export").mock(
            return_value=Response(200)
        )

        await client.export()

        assert route.called
        await client.transport.close()
