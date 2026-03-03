"""Tests for AppDBClient with mocked transport."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

from domo_sdk.clients.appdb import AppDBClient
from domo_sdk.models.appdb import (
    AppDBCollection,
    AppDBDocument,
    BulkOperationResult,
)


def _make_client() -> tuple[AppDBClient, MagicMock]:
    """Create an AppDBClient with a fully mocked transport."""
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    client = AppDBClient(transport)
    return client, transport


# --- Collection operations ---


class TestCollectionOperations:
    """Tests for collection CRUD."""

    def test_create_collection(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": "col-1",
            "name": "my-collection",
            "datastoreId": "ds-1",
            "syncEnabled": False,
        }

        result = client.create_collection("my-collection")

        transport.post.assert_called_once_with(
            "/datastores/v1/collections",
            body={"name": "my-collection", "syncEnabled": False},
            params=None,
        )
        assert isinstance(result, AppDBCollection)
        assert result.name == "my-collection"

    def test_create_collection_with_schema(self) -> None:
        client, transport = _make_client()
        schema = {"columns": [{"type": "STRING", "name": "title"}]}
        transport.post.return_value = {
            "id": "col-1",
            "name": "test",
            "datastoreId": "ds-1",
            "schema": schema,
        }

        result = client.create_collection("test", schema=schema, sync_enabled=True)

        call_body = transport.post.call_args.kwargs["body"]
        assert call_body["schema"] == schema
        assert call_body["syncEnabled"] is True
        assert result.schema_ is not None

    def test_get_collection(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": "col-1",
            "name": "my-collection",
            "datastoreId": "ds-1",
        }

        result = client.get_collection("col-1")

        transport.get.assert_called_once_with(
            "/datastores/v1/collections/col-1",
            params=None,
        )
        assert isinstance(result, AppDBCollection)
        assert result.id == "col-1"

    def test_list_collections(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": "col-1", "name": "first"},
            {"id": "col-2", "name": "second"},
        ]

        result = client.list_collections()

        transport.get.assert_called_once_with(
            "/datastores/v1/collections",
            params=None,
        )
        assert len(result) == 2
        assert all(isinstance(c, AppDBCollection) for c in result)

    def test_update_collection(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {
            "id": "col-1",
            "name": "updated-name",
            "datastoreId": "ds-1",
        }

        result = client.update_collection("col-1", {"name": "updated-name"})

        transport.put.assert_called_once_with(
            "/datastores/v1/collections/col-1",
            body={"name": "updated-name"},
            params=None,
        )
        assert isinstance(result, AppDBCollection)
        assert result.name == "updated-name"

    def test_delete_collection(self) -> None:
        client, transport = _make_client()

        client.delete_collection("col-1")

        transport.delete.assert_called_once_with(
            "/datastores/v1/collections/col-1",
            params=None,
        )


# --- Document operations ---


class TestDocumentOperations:
    """Tests for document CRUD."""

    def test_create_document(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": "doc-1",
            "datastoreId": "ds-1",
            "collectionId": "col-1",
            "content": {"title": "Hello"},
            "owner": 123,
        }

        result = client.create_document("col-1", {"title": "Hello"})

        transport.post.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents",
            body={"content": {"title": "Hello"}},
            params=None,
        )
        assert isinstance(result, AppDBDocument)
        assert result.content["title"] == "Hello"

    def test_get_document(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": "doc-1",
            "content": {"key": "value"},
            "datastoreId": "ds-1",
            "collectionId": "col-1",
            "owner": 123,
        }

        result = client.get_document("col-1", "doc-1")

        transport.get.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents/doc-1",
            params=None,
        )
        assert isinstance(result, AppDBDocument)
        assert result.id == "doc-1"
        assert result.content == {"key": "value"}

    def test_list_documents(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": "doc-1", "content": {"a": 1}},
            {"id": "doc-2", "content": {"b": 2}},
        ]

        result = client.list_documents("col-1")

        transport.get.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents",
            params=None,
        )
        assert len(result) == 2
        assert all(isinstance(d, AppDBDocument) for d in result)

    def test_update_document(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {
            "id": "doc-1",
            "datastoreId": "ds-1",
            "collectionId": "col-1",
            "content": {"title": "Updated"},
        }

        result = client.update_document("col-1", "doc-1", {"title": "Updated"})

        transport.put.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents/doc-1",
            body={"content": {"title": "Updated"}},
            params=None,
        )
        assert isinstance(result, AppDBDocument)
        assert result.content["title"] == "Updated"

    def test_delete_document(self) -> None:
        client, transport = _make_client()

        client.delete_document("col-1", "doc-1")

        transport.delete.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents/doc-1",
            params=None,
        )


# --- Query ---


class TestQueryOperations:
    """Tests for query with v2 endpoint."""

    def test_query_basic(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = [
            {"id": "doc-1", "content": {"status": "active"}},
        ]

        q = {"content.status": {"$eq": "active"}}
        result = client.query("col-1", q)

        transport.post.assert_called_once_with(
            "/datastores/v2/collections/col-1/documents/query",
            body=q,
            params={},
        )
        assert len(result) == 1
        assert isinstance(result[0], AppDBDocument)

    def test_query_with_pagination(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = []

        client.query("col-1", {}, limit=10, offset=20, order_by="content.created")

        transport.post.assert_called_once_with(
            "/datastores/v2/collections/col-1/documents/query",
            body={},
            params={"limit": 10, "offset": 20, "orderBy": "content.created"},
        )

    def test_query_with_aggregation(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = []

        client.query(
            "col-1",
            {},
            group_by="content.category",
            count="content.id",
            sum="content.amount",
        )

        _, kwargs = transport.post.call_args
        assert kwargs["params"]["groupby"] == "content.category"
        assert kwargs["params"]["count"] == "content.id"
        assert kwargs["params"]["sum"] == "content.amount"

    def test_query_empty_result(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = []

        result = client.query("col-1", {"content.x": {"$eq": "nonexistent"}})

        assert result == []


# --- Bulk operations ---


class TestBulkOperations:
    """Tests for bulk create/upsert/delete."""

    def test_bulk_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {"Created": 3, "Updated": 0, "Deleted": 0}

        docs = [{"title": "A"}, {"title": "B"}, {"title": "C"}]
        result = client.bulk_create("col-1", docs)

        transport.post.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents/bulk",
            body=[{"content": {"title": "A"}}, {"content": {"title": "B"}}, {"content": {"title": "C"}}],
            params=None,
        )
        assert isinstance(result, BulkOperationResult)
        assert result.created == 3

    def test_bulk_upsert(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {"Created": 1, "Updated": 2}

        docs = [{"id": "existing", "title": "X"}, {"title": "New"}]
        result = client.bulk_upsert("col-1", docs)

        transport.put.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents/bulk",
            body=docs,
            params=None,
        )
        assert isinstance(result, BulkOperationResult)
        assert result.created == 1
        assert result.updated == 2

    def test_bulk_delete(self) -> None:
        client, transport = _make_client()
        transport.delete.return_value = {"Deleted": 3}

        result = client.bulk_delete("col-1", ["id-1", "id-2", "id-3"])

        transport.delete.assert_called_once_with(
            "/datastores/v1/collections/col-1/documents/bulk",
            params={"ids": "id-1,id-2,id-3"},
        )
        assert isinstance(result, BulkOperationResult)
        assert result.deleted == 3


# --- Partial update ---


class TestPartialUpdate:
    """Tests for partial_update with MongoDB operators."""

    def test_partial_update(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {"Created": 0, "Updated": 5, "Deleted": 0}

        q = {"content.status": {"$eq": "active"}}
        op = {"$set": {"content.status": "inactive"}}
        result = client.partial_update("col-1", q, op)

        call_body = transport.put.call_args.kwargs["body"]
        assert json.loads(call_body["query"]) == q
        assert json.loads(call_body["operation"]) == op
        assert isinstance(result, BulkOperationResult)
        assert result.updated == 5


# --- Permissions ---


class TestPermissions:
    """Tests for permission management."""

    def test_set_permission(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = None

        client.set_permission("col-1", "USER", "123", ["read", "write"])

        transport.put.assert_called_once_with(
            "/datastores/v1/collections/col-1/permission/USER/123",
            body=None,
            params={"permissions": "read,write"},
        )

    def test_remove_permission(self) -> None:
        client, transport = _make_client()

        client.remove_permission("col-1", "GROUP", "456")

        transport.delete.assert_called_once_with(
            "/datastores/v1/collections/col-1/permission/GROUP/456",
            params=None,
        )


# --- Export ---


class TestExport:
    """Tests for export trigger."""

    def test_export(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = None

        client.export()

        transport.post.assert_called_once_with(
            "/datastores/v1/export",
            body=None,
            params=None,
        )
