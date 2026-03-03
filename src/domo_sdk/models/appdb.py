"""AppDB (document store) models."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel
from domo_sdk.models.datasets import ColumnType


class SchemaColumn(DomoModel):
    """Column definition in a collection schema."""

    type: ColumnType
    name: str
    visible: bool = True


class CollectionSchema(DomoModel):
    """Collection schema."""

    columns: list[SchemaColumn] = Field(default_factory=list)


class AppDBCollection(DomoModel):
    """AppDB collection."""

    id: str = ""
    datastore_id: str = Field(default="", alias="datastoreId")
    name: str = ""
    owner: int = 0
    schema_: CollectionSchema | None = Field(default=None, alias="schema")
    sync_enabled: bool = Field(default=False, alias="syncEnabled")
    sync_required: bool = Field(default=False, alias="syncRequired")
    full_replace_required: bool = Field(default=False, alias="fullReplaceRequired")
    last_sync: datetime | None = Field(default=None, alias="lastSync")
    created_on: datetime | None = Field(default=None, alias="createdOn")
    updated_on: datetime | None = Field(default=None, alias="updatedOn")
    updated_by: int = Field(default=0, alias="updatedBy")


class AppDBDocument(DomoModel):
    """AppDB document."""

    id: str = ""
    datastore_id: str = Field(default="", alias="datastoreId")
    collection_id: str = Field(default="", alias="collectionId")
    content: dict[str, Any] = Field(default_factory=dict)
    owner: int = 0
    created_by: int = Field(default=0, alias="createdBy")
    created_on: datetime | None = Field(default=None, alias="createdOn")
    updated_on: datetime | None = Field(default=None, alias="updatedOn")
    updated_by: int = Field(default=0, alias="updatedBy")


class BulkOperationResult(DomoModel):
    """Result of a bulk create/upsert/delete operation."""

    created: int = Field(default=0, alias="Created")
    updated: int = Field(default=0, alias="Updated")
    deleted: int = Field(default=0, alias="Deleted")
