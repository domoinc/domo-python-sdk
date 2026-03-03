"""Tests for AsyncDataSetClient using respx to mock httpx requests."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.datasets import AsyncDataSetClient
from domo_sdk.models.datasets import (
    DataSet,
    DataSetPermission,
    DataVersion,
    Index,
    Partition,
    Policy,
    QueryResult,
    Schema,
    UploadSession,
)
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import DeveloperTokenCredentials, DeveloperTokenStrategy


def _make_async_client() -> tuple[AsyncDataSetClient, str]:
    """Create an AsyncDataSetClient backed by a real AsyncTransport."""
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncDataSetClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncDataSetCRUD:
    """Async dataset CRUD tests."""

    @respx.mock
    async def test_create_dataset(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(f"{base_url}/v1/datasets").mock(
            return_value=Response(
                200, json={"id": "new-ds", "name": "Test"}
            )
        )

        result = await client.create({"name": "Test"})

        assert route.called
        assert isinstance(result, DataSet)
        assert result.id == "new-ds"
        await client.transport.close()

    @respx.mock
    async def test_get_dataset(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(f"{base_url}/v1/datasets/ds-123").mock(
            return_value=Response(
                200, json={"id": "ds-123", "name": "Sales"}
            )
        )

        result = await client.get("ds-123")

        assert route.called
        assert isinstance(result, DataSet)
        assert result.id == "ds-123"
        assert result.name == "Sales"
        await client.transport.close()

    @respx.mock
    async def test_list_datasets(self) -> None:
        client, base_url = _make_async_client()
        respx.get(f"{base_url}/v1/datasets").mock(
            side_effect=[
                Response(
                    200,
                    json=[
                        {"id": "ds-1", "name": "A"},
                        {"id": "ds-2", "name": "B"},
                    ],
                ),
                Response(200, json=[]),
            ]
        )

        result = await client.list(per_page=2)

        assert len(result) == 2
        assert all(isinstance(r, DataSet) for r in result)
        assert result[0].id == "ds-1"
        await client.transport.close()

    @respx.mock
    async def test_update_dataset(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(f"{base_url}/v1/datasets/ds-123").mock(
            return_value=Response(
                200, json={"id": "ds-123", "name": "Updated"}
            )
        )

        result = await client.update("ds-123", {"name": "Updated"})

        assert route.called
        assert isinstance(result, DataSet)
        assert result.name == "Updated"
        await client.transport.close()

    @respx.mock
    async def test_delete_dataset(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(f"{base_url}/v1/datasets/ds-123").mock(
            return_value=Response(204)
        )

        await client.delete("ds-123")

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetQuery:
    """Async query tests."""

    @respx.mock
    async def test_query(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/datasets/query/execute/ds-123"
        ).mock(
            return_value=Response(
                200,
                json={
                    "columns": ["name", "revenue"],
                    "rows": [["Alice", "1000"]],
                    "numRows": 1,
                    "numColumns": 2,
                },
            )
        )

        result = await client.query(
            "ds-123", "SELECT name, revenue FROM sales"
        )

        assert route.called
        assert isinstance(result, QueryResult)
        assert result.num_rows == 1
        assert result.columns == ["name", "revenue"]
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetSchema:
    """Async schema and metadata tests."""

    @respx.mock
    async def test_get_schema(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/data/v2/datasources/ds-123/schemas/latest"
        ).mock(
            return_value=Response(
                200,
                json={
                    "columns": [{"type": "STRING", "name": "col1"}]
                },
            )
        )

        result = await client.get_schema("ds-123")

        assert route.called
        assert isinstance(result, Schema)
        assert len(result.columns) == 1
        await client.transport.close()

    @respx.mock
    async def test_get_metadata(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/data/v3/datasources/ds-123"
        ).mock(
            return_value=Response(
                200, json={"id": "ds-123", "name": "Sales"}
            )
        )

        result = await client.get_metadata("ds-123")

        assert route.called
        assert isinstance(result, DataSet)
        assert result.id == "ds-123"
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetPermissions:
    """Async permission and sharing tests."""

    @respx.mock
    async def test_get_permissions(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/data/v3/datasources/ds-123/permissions"
        ).mock(
            return_value=Response(
                200,
                json=[
                    {"id": 42, "type": "USER", "permissions": ["READ"]},
                ],
            )
        )

        result = await client.get_permissions("ds-123")

        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], DataSetPermission)
        assert result[0].id == 42
        await client.transport.close()

    @respx.mock
    async def test_share(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/data/v3/datasources/ds-123/share"
        ).mock(return_value=Response(200, json={}))

        await client.share(
            "ds-123",
            [{"id": 42, "type": "USER", "accessLevel": "READ"}],
        )

        assert route.called
        await client.transport.close()

    @respx.mock
    async def test_revoke_access(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(
            f"{base_url}/data/v3/datasources/ds-123/permissions/USER/42"
        ).mock(return_value=Response(204))

        await client.revoke_access("ds-123", 42)

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetTags:
    """Async tag tests."""

    @respx.mock
    async def test_set_tags(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/data/ui/v3/datasources/ds-123/tags"
        ).mock(return_value=Response(200, json={}))

        await client.set_tags("ds-123", ["sales", "q4"])

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetPDP:
    """Async PDP tests."""

    @respx.mock
    async def test_create_pdp(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/datasets/ds-123/policies"
        ).mock(
            return_value=Response(
                200,
                json={"id": 1, "name": "My Policy", "type": "user"},
            )
        )

        result = await client.create_pdp(
            "ds-123", {"name": "My Policy"}
        )

        assert route.called
        assert isinstance(result, Policy)
        assert result.name == "My Policy"
        await client.transport.close()

    @respx.mock
    async def test_list_pdps(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/v1/datasets/ds-123/policies"
        ).mock(
            return_value=Response(
                200,
                json=[
                    {"id": 1, "name": "P1", "type": "user"},
                    {"id": 2, "name": "P2", "type": "user"},
                ],
            )
        )

        result = await client.list_pdps("ds-123")

        assert route.called
        assert len(result) == 2
        assert all(isinstance(p, Policy) for p in result)
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetVersions:
    """Async version and index tests."""

    @respx.mock
    async def test_list_versions(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/data/v3/datasources/ds-123/dataversions/details"
        ).mock(
            return_value=Response(
                200,
                json=[
                    {"versionId": "v1", "rowCount": 100},
                    {"versionId": "v2", "rowCount": 200},
                ],
            )
        )

        result = await client.list_versions("ds-123")

        assert route.called
        assert len(result) == 2
        assert all(isinstance(v, DataVersion) for v in result)
        assert result[0].version_id == "v1"
        await client.transport.close()

    @respx.mock
    async def test_create_index(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/data/v3/datasources/ds-123/indexes"
        ).mock(
            return_value=Response(
                200, json={"columns": ["col1", "col2"]}
            )
        )

        result = await client.create_index("ds-123", ["col1", "col2"])

        assert route.called
        assert isinstance(result, Index)
        assert result.columns == ["col1", "col2"]
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetPartitions:
    """Async partition tests."""

    @respx.mock
    async def test_list_partitions(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/api/query/v1/datasources/ds-123/partition"
        ).mock(
            return_value=Response(
                200,
                json=[
                    {"partitionId": "2024-01", "name": "Jan 2024"},
                    {"partitionId": "2024-02", "name": "Feb 2024"},
                ],
            )
        )

        result = await client.list_partitions("ds-123")

        assert route.called
        assert len(result) == 2
        assert all(isinstance(p, Partition) for p in result)
        assert result[0].partition_id == "2024-01"
        await client.transport.close()

    @respx.mock
    async def test_delete_partition(self) -> None:
        client, base_url = _make_async_client()
        route = respx.delete(
            f"{base_url}/api/query/v1/datasources/ds-123/partition/2024-01"
        ).mock(return_value=Response(204))

        await client.delete_partition("ds-123", "2024-01")

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetUploadSessions:
    """Async upload session tests."""

    @respx.mock
    async def test_create_upload_session(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/data/v3/datasources/ds-123/uploads"
        ).mock(
            return_value=Response(200, json={"uploadId": 42})
        )

        result = await client.create_upload_session("ds-123")

        assert route.called
        assert isinstance(result, UploadSession)
        assert result.upload_id == 42
        await client.transport.close()

    @respx.mock
    async def test_commit_upload(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(
            f"{base_url}/data/v3/datasources/ds-123/uploads/42/commit"
        ).mock(return_value=Response(200, json={}))

        await client.commit_upload("ds-123", 42)

        assert route.called
        await client.transport.close()


@pytest.mark.asyncio
class TestAsyncDataSetProperties:
    """Async properties tests."""

    @respx.mock
    async def test_set_properties(self) -> None:
        client, base_url = _make_async_client()
        route = respx.put(
            f"{base_url}/data/v3/datasources/ds-123/properties"
        ).mock(return_value=Response(200, json={}))

        await client.set_properties(
            "ds-123", {"dataProviderType": "custom"}
        )

        assert route.called
        await client.transport.close()
