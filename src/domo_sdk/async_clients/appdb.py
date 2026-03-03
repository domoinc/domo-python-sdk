"""Async AppDB client for the Domo API."""
from __future__ import annotations

import json
from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.appdb import (
    AppDBCollection,
    AppDBDocument,
    BulkOperationResult,
)

URL_BASE = "/datastores/v1/collections"
URL_BASE_V2 = "/datastores/v2/collections"


class AsyncAppDBClient(AsyncDomoAPIClient):
    """Manage AppDB collections and documents asynchronously.

    AppDB is Domo's NoSQL document store for custom apps.
    Requires Developer Token authentication.

    Docs: https://developer.domo.com/docs/appdb-api-reference
    """

    # --- Collection operations ---

    async def create_collection(
        self,
        name: str,
        schema: dict[str, Any] | None = None,
        sync_enabled: bool = False,
    ) -> AppDBCollection:
        """Create a new collection."""
        body: dict[str, Any] = {"name": name, "syncEnabled": sync_enabled}
        if schema:
            body["schema"] = schema
        result = await self._create(URL_BASE, body)
        return AppDBCollection.model_validate(result)

    async def get_collection(self, collection_id: str) -> AppDBCollection:
        """Get a collection by name or ID."""
        result = await self._get(f"{URL_BASE}/{collection_id}")
        return AppDBCollection.model_validate(result)

    async def list_collections(self) -> list[AppDBCollection]:
        """List all collections."""
        result = await self._list(URL_BASE)
        return [AppDBCollection.model_validate(c) for c in result]

    async def update_collection(
        self,
        collection_id: str,
        update_data: dict[str, Any],
    ) -> AppDBCollection:
        """Update a collection (schema, sync settings)."""
        result = await self._update(f"{URL_BASE}/{collection_id}", update_data)
        return AppDBCollection.model_validate(result)

    async def delete_collection(self, collection_id: str) -> None:
        """Delete a collection and all its documents."""
        await self._delete(f"{URL_BASE}/{collection_id}")

    # --- Document operations ---

    async def create_document(
        self,
        collection_id: str,
        content: dict[str, Any],
    ) -> AppDBDocument:
        """Create a document in a collection."""
        result = await self._create(
            f"{URL_BASE}/{collection_id}/documents",
            {"content": content},
        )
        return AppDBDocument.model_validate(result)

    async def get_document(
        self,
        collection_id: str,
        document_id: str,
    ) -> AppDBDocument:
        """Get a document by ID."""
        result = await self._get(
            f"{URL_BASE}/{collection_id}/documents/{document_id}"
        )
        return AppDBDocument.model_validate(result)

    async def list_documents(self, collection_id: str) -> list[AppDBDocument]:
        """List all documents in a collection.

        Note: Hard limit of 10,000 documents. For larger collections,
        use query() with limit/offset for pagination.
        """
        result = await self._list(f"{URL_BASE}/{collection_id}/documents")
        return [AppDBDocument.model_validate(d) for d in result]

    async def update_document(
        self,
        collection_id: str,
        document_id: str,
        content: dict[str, Any],
    ) -> AppDBDocument:
        """Replace a document's content."""
        result = await self._update(
            f"{URL_BASE}/{collection_id}/documents/{document_id}",
            {"content": content},
        )
        return AppDBDocument.model_validate(result)

    async def delete_document(
        self,
        collection_id: str,
        document_id: str,
    ) -> None:
        """Delete a document."""
        await self._delete(
            f"{URL_BASE}/{collection_id}/documents/{document_id}"
        )

    # --- Query ---

    async def query(
        self,
        collection_id: str,
        query: dict[str, Any],
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        group_by: str | None = None,
        count: str | None = None,
        avg: str | None = None,
        min: str | None = None,
        max: str | None = None,
        sum: str | None = None,
    ) -> list[AppDBDocument]:
        """Query documents using MongoDB-style syntax.

        Args:
            collection_id: Collection name or ID.
            query: MongoDB-style query dict,
                e.g. ``{"content.status": {"$eq": "active"}}``.
            limit: Max documents to return.
            offset: Number of documents to skip.
            order_by: Field to sort by, e.g. ``"content.created_at"``.
            group_by: Field to group results by.
            count: Field to count.
            avg: Field to average.
            min: Field to find minimum.
            max: Field to find maximum.
            sum: Field to sum.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if order_by is not None:
            params["orderBy"] = order_by
        if group_by is not None:
            params["groupby"] = group_by
        if count is not None:
            params["count"] = count
        if avg is not None:
            params["avg"] = avg
        if min is not None:
            params["min"] = min
        if max is not None:
            params["max"] = max
        if sum is not None:
            params["sum"] = sum

        result = await self.transport.post(
            f"{URL_BASE_V2}/{collection_id}/documents/query",
            body=query,
            params=params,
        )
        return [AppDBDocument.model_validate(d) for d in result]

    # --- Bulk operations ---

    async def bulk_create(
        self,
        collection_id: str,
        documents: list[dict[str, Any]],
    ) -> BulkOperationResult:
        """Create multiple documents at once."""
        body = [{"content": doc} for doc in documents]
        result = await self._create(
            f"{URL_BASE}/{collection_id}/documents/bulk", body
        )
        return BulkOperationResult.model_validate(result)

    async def bulk_upsert(
        self,
        collection_id: str,
        documents: list[dict[str, Any]],
    ) -> BulkOperationResult:
        """Create or update multiple documents.

        Documents with an 'id' key are updated; those without are created.
        """
        result = await self._update(
            f"{URL_BASE}/{collection_id}/documents/bulk", documents
        )
        return BulkOperationResult.model_validate(result)

    async def bulk_delete(
        self,
        collection_id: str,
        document_ids: list[str],
    ) -> BulkOperationResult:
        """Delete multiple documents by ID.

        Note: IDs are passed as query params. For very large lists
        (500+ UUIDs), batch your calls to avoid URL length limits.
        """
        ids_str = ",".join(document_ids)
        result = await self._delete(
            f"{URL_BASE}/{collection_id}/documents/bulk",
            params={"ids": ids_str},
        )
        return BulkOperationResult.model_validate(result)

    # --- Partial update ---

    async def partial_update(
        self,
        collection_id: str,
        query: dict[str, Any],
        operation: dict[str, Any],
    ) -> BulkOperationResult:
        """Update fields on documents matching a query.

        Uses MongoDB-style update operators ($set, $unset, $inc, etc.).

        Warning: An empty query ``{}`` matches ALL documents in the collection.

        Args:
            collection_id: Collection name or ID.
            query: MongoDB-style filter,
                e.g. ``{"content.status": {"$eq": "active"}}``.
            operation: Update operation,
                e.g. ``{"$set": {"content.status": "inactive"}}``.
        """
        body = {
            "query": json.dumps(query),
            "operation": json.dumps(operation),
        }
        result = await self._update(
            f"{URL_BASE}/{collection_id}/documents/update", body
        )
        return BulkOperationResult.model_validate(result)

    # --- Permissions ---

    async def set_permission(
        self,
        collection_id: str,
        entity_type: str,
        entity_id: str,
        permissions: list[str],
    ) -> None:
        """Set permissions on a collection.

        Args:
            collection_id: Collection name or ID.
            entity_type: ``"USER"``, ``"GROUP"``, or ``"RYUU_APP"``.
            entity_id: The user, group, or app proxy ID.
            permissions: List of permissions
                (e.g. ``["read", "write"]``).
        """
        url = (
            f"{URL_BASE}/{collection_id}"
            f"/permission/{entity_type}/{entity_id}"
        )
        await self._update(
            url,
            body=None,
            params={"permissions": ",".join(permissions)},
        )

    async def remove_permission(
        self,
        collection_id: str,
        entity_type: str,
        entity_id: str,
    ) -> None:
        """Remove all permissions for an entity on a collection."""
        await self._delete(
            f"{URL_BASE}/{collection_id}"
            f"/permission/{entity_type}/{entity_id}"
        )

    # --- Export ---

    async def export(self) -> None:
        """Trigger a manual export of all AppDB data to datasets.

        Raises DomoAPIError with status 423 if an export is already
        in progress.
        """
        await self._create("/datastores/v1/export", body=None)
