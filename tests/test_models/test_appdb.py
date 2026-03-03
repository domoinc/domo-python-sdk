"""Tests for AppDB models."""
from __future__ import annotations

from domo_sdk.models.appdb import (
    AppDBCollection,
    AppDBDocument,
    BulkOperationResult,
    CollectionSchema,
    SchemaColumn,
)
from domo_sdk.models.datasets import ColumnType


class TestSchemaColumn:
    """Tests for SchemaColumn model."""

    def test_schema_column(self) -> None:
        col = SchemaColumn(type=ColumnType.STRING, name="title")
        assert col.type == ColumnType.STRING
        assert col.name == "title"
        assert col.visible is True

    def test_schema_column_hidden(self) -> None:
        col = SchemaColumn(type=ColumnType.LONG, name="internal_id", visible=False)
        assert col.visible is False


class TestCollectionSchema:
    """Tests for CollectionSchema model."""

    def test_empty_schema(self) -> None:
        schema = CollectionSchema()
        assert schema.columns == []

    def test_schema_with_columns(self) -> None:
        data = {
            "columns": [
                {"type": "STRING", "name": "title"},
                {"type": "LONG", "name": "count", "visible": False},
            ]
        }
        schema = CollectionSchema.model_validate(data)
        assert len(schema.columns) == 2
        assert schema.columns[0].type == ColumnType.STRING
        assert schema.columns[1].visible is False

    def test_mutable_default_columns(self) -> None:
        """Verify default_factory creates independent lists."""
        s1 = CollectionSchema()
        s2 = CollectionSchema()
        s1.columns.append(SchemaColumn(type=ColumnType.STRING, name="x"))
        assert len(s2.columns) == 0


class TestAppDBCollection:
    """Tests for AppDBCollection model."""

    def test_collection_from_api_response(self) -> None:
        data = {
            "id": "col-123",
            "datastoreId": "ds-456",
            "name": "my-collection",
            "owner": 12345,
            "schema": {
                "columns": [{"type": "STRING", "name": "title"}]
            },
            "syncEnabled": True,
            "syncRequired": False,
            "fullReplaceRequired": False,
            "lastSync": "2024-05-08T19:39:00.708Z",
            "createdOn": "2024-01-01T00:00:00Z",
            "updatedOn": "2024-06-01T12:00:00Z",
            "updatedBy": 67890,
        }
        col = AppDBCollection.model_validate(data)
        assert col.id == "col-123"
        assert col.datastore_id == "ds-456"
        assert col.name == "my-collection"
        assert col.owner == 12345
        assert col.sync_enabled is True
        assert col.schema_ is not None
        assert len(col.schema_.columns) == 1
        assert col.updated_by == 67890

    def test_collection_defaults(self) -> None:
        col = AppDBCollection()
        assert col.id == ""
        assert col.name == ""
        assert col.owner == 0
        assert col.schema_ is None
        assert col.sync_enabled is False

    def test_collection_ignores_unknown_fields(self) -> None:
        data = {"id": "col-1", "name": "test", "unknownField": "ignored"}
        col = AppDBCollection.model_validate(data)
        assert col.id == "col-1"


class TestAppDBDocument:
    """Tests for AppDBDocument model."""

    def test_document_from_api_response(self) -> None:
        data = {
            "id": "abc-123",
            "datastoreId": "ds-456",
            "collectionId": "col-789",
            "content": {"name": "Widget", "price": 9.99},
            "owner": 12345,
            "createdBy": 12345,
            "createdOn": "2024-05-08T19:39:00.708Z",
            "updatedOn": "2024-06-01T12:00:00Z",
            "updatedBy": 67890,
        }
        doc = AppDBDocument.model_validate(data)
        assert doc.id == "abc-123"
        assert doc.content["name"] == "Widget"
        assert doc.collection_id == "col-789"
        assert doc.owner == 12345
        assert doc.created_by == 12345
        assert doc.updated_by == 67890

    def test_document_defaults(self) -> None:
        doc = AppDBDocument()
        assert doc.id == ""
        assert doc.content == {}
        assert doc.owner == 0

    def test_mutable_default_content(self) -> None:
        """Verify default_factory creates independent dicts."""
        doc1 = AppDBDocument()
        doc2 = AppDBDocument()
        doc1.content["key"] = "value"
        assert "key" not in doc2.content

    def test_document_serialization_round_trip(self) -> None:
        data = {
            "id": "doc-1",
            "datastoreId": "ds-1",
            "collectionId": "col-1",
            "content": {"nested": {"deep": True}},
            "owner": 1,
            "createdBy": 1,
        }
        doc = AppDBDocument.model_validate(data)
        dumped = doc.model_dump(by_alias=True)
        assert dumped["datastoreId"] == "ds-1"
        assert dumped["collectionId"] == "col-1"
        assert dumped["content"]["nested"]["deep"] is True


class TestBulkOperationResult:
    """Tests for BulkOperationResult model."""

    def test_bulk_create_response(self) -> None:
        data = {"Created": 5, "Updated": 0, "Deleted": 0}
        result = BulkOperationResult.model_validate(data)
        assert result.created == 5
        assert result.updated == 0
        assert result.deleted == 0

    def test_bulk_upsert_response(self) -> None:
        data = {"Created": 2, "Updated": 3}
        result = BulkOperationResult.model_validate(data)
        assert result.created == 2
        assert result.updated == 3
        assert result.deleted == 0  # default

    def test_bulk_delete_response(self) -> None:
        data = {"Deleted": 10}
        result = BulkOperationResult.model_validate(data)
        assert result.deleted == 10
        assert result.created == 0  # default

    def test_defaults(self) -> None:
        result = BulkOperationResult()
        assert result.created == 0
        assert result.updated == 0
        assert result.deleted == 0
