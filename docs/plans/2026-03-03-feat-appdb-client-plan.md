---
title: "feat: Add AppDB client"
type: feat
status: completed
date: 2026-03-03
brainstorm: docs/brainstorms/2026-03-03-expand-api-coverage-brainstorm.md
---

# feat: Add AppDB Client

## Enhancement Summary

**Deepened on:** 2026-03-03
**Sections enhanced:** 8
**Review agents used:** kieran-python-reviewer, architecture-strategist, pattern-recognition-specialist, performance-oracle, security-sentinel, code-simplicity-reviewer, best-practices-researcher

### Key Improvements

1. **Prerequisite PR identified** — Transport layer needs `params` support on `put()`/`delete()` and `delete()` must return response body. Without this, `set_permission` and `bulk_delete` are broken at runtime.
2. **Model code revised** — Mutable default fixes (`Field(default_factory=...)`), `ColumnType` reuse from datasets, unused enums removed, `owner` type inconsistency fixed.
3. **Client code revised** — `**aggregation` kwargs replaced with explicit params, `partial_update` returns model, `set_permission` actually sends permissions, `import json` moved to module level, v2 URL extracted to constant.
4. **Security hardening** — Path parameter validation, restricted aggregation keys, empty-query guard on `partial_update`.
5. **Performance guidance** — `TypeAdapter` for list deserialization, document 10K limit, chunk guidance for bulk ops.

### Resolved Open Questions

- **Q1 (URL_BASE):** Still requires curl validation — cannot resolve without live API call.
- **Q2 (`_update` params):** Confirmed `_update` does NOT support `params`. Requires prerequisite PR.
- **Q3 (`transport.delete` params/return):** Confirmed `delete()` takes no `params` AND returns `None`. Requires prerequisite PR.

---

## Overview

Add a complete AppDB (document store) client to the SDK — the first new client in the broader API expansion effort. This is also the **first client to return Pydantic models by default**, establishing the pattern all future clients will follow.

AppDB is Domo's NoSQL document store for custom apps. It supports collections (like tables) containing JSON documents, with MongoDB-style querying, bulk operations, and permission management.

## Problem Statement

The SDK has no AppDB support. WKS is building Domo apps that need document storage, and there's no Python SDK to interact with AppDB programmatically from outside Domo apps.

## Proposed Solution

Add 7 files following the established per-client pattern, with one key evolution: **methods return Pydantic models instead of raw dicts**.

**This requires a prerequisite PR** to fix transport layer gaps before the AppDB client can be fully functional.

### Phase 0: Prerequisite — Transport `params` Support (Separate PR)

The current transport layer has two gaps that block AppDB's `set_permission` and `bulk_delete` methods:

| Gap | Current | Needed | Files |
|-----|---------|--------|-------|
| `put()` lacks `params` | `put(url, body)` | `put(url, body, params)` | `sync_transport.py:118`, `async_transport.py:140` |
| `delete()` lacks `params` + returns `None` | `delete(url) -> None` | `delete(url, params) -> Any` | `sync_transport.py:152`, `async_transport.py:174` |
| `_update` helper lacks `params` | `_update(url, body, method)` | `_update(url, body, method, params)` | `clients/base.py:32`, `async_clients/base.py:32` |
| `_delete` helper lacks `params` + returns `None` | `_delete(url) -> None` | `_delete(url, params) -> Any` | `clients/base.py:37`, `async_clients/base.py:37` |

**Implementation:** Mirror the pattern already used by `post()` and `get()` — add optional `params: dict[str, Any] | None = None` and pass through to `requests`/`httpx`. For `delete()`, return `response.json()` when body is present (same pattern as `put()`).

**Scope:** 4 files changed, backward-compatible (new param is optional with default `None`). Ship as its own PR before AppDB.

### Pre-Implementation: Validate URL Routing

Before writing any code, verify the AppDB API path works through the transport layer:

```bash
# Test with a real developer token
curl -s -X GET "https://wksusa.domo.com/api/datastores/v1/collections/" \
  -H "X-DOMO-Developer-Token: $DOMO_DEVELOPER_TOKEN" \
  -H "Accept: application/json"
```

If the path is wrong (404), try without `/api` prefix:
```bash
curl -s -X GET "https://wksusa.domo.com/domo/datastores/v1/collections/" \
  -H "X-DOMO-Developer-Token: $DOMO_DEVELOPER_TOKEN"
```

This determines the `URL_BASE` constant. The transport's `DeveloperTokenStrategy.get_base_url()` returns `https://{domain}/api`, so if the API lives at `https://instance.domo.com/api/datastores/v1/...`, then `URL_BASE = "/datastores/v1/collections"`.

### Design Decision: Pydantic Model Returns

Since this is the first client to return models, the pattern must be simple and replicable:

**Approach: Inline `model_validate()` in each method.**

```python
def get(self, collection_id: str, document_id: str) -> AppDBDocument:
    result = self._get(f"{URL_BASE}/{collection_id}/documents/{document_id}")
    return AppDBDocument.model_validate(result)

def list_documents(self, collection_id: str) -> list[AppDBDocument]:
    result = self._list(f"{URL_BASE}/{collection_id}/documents")
    return [AppDBDocument.model_validate(d) for d in result]
```

Why inline rather than a base class helper:
- Explicit — you can see exactly what model is returned
- No new abstraction to learn
- Easy to customize per-method (some methods return lists, some single objects, some have special handling)
- The base class stays unchanged — zero impact on existing clients

For void methods (`delete`, `remove_permission`), continue returning `None`.

#### Research Insights: Model Returns

**Best Practices (OpenAI/Anthropic SDK patterns):**
- OpenAI SDK uses `cast_to: Type[T]` in base class — works well but adds abstraction. Our inline approach is simpler for a first client; can adopt `cast_to` later if boilerplate grows.
- Use `TypeAdapter` for list deserialization when performance matters (15-30% faster than per-item `model_validate` at 1000+ items). Consider for `list_documents` and `query`.

```python
from pydantic import TypeAdapter

_DOCUMENT_LIST_ADAPTER = TypeAdapter(list[AppDBDocument])

def list_documents(self, collection_id: str) -> list[AppDBDocument]:
    result = self._list(f"{URL_BASE}/{collection_id}/documents")
    return _DOCUMENT_LIST_ADAPTER.validate_python(result)
```

**Decision:** Start with simple `model_validate()` loops. Add `TypeAdapter` optimization if profiling shows it matters (10K document collections are the threshold).

## Technical Approach

### File Map

| # | File | Purpose |
|---|------|---------|
| 0 | Transport prerequisite PR (4 files) | Add `params` to `put()`/`delete()`, return body from `delete()` |
| 1 | `src/domo_sdk/models/appdb.py` | Pydantic models for collections, documents, query results |
| 2 | `src/domo_sdk/clients/appdb.py` | Sync client (~15 methods) |
| 3 | `src/domo_sdk/async_clients/appdb.py` | Async mirror |
| 4 | `src/domo_sdk/domo.py` | Wire `self.appdb` in both `Domo` and `AsyncDomo._init_clients()` |
| 5 | `tests/test_models/test_appdb.py` | Model validation tests |
| 6 | `tests/test_clients/test_appdb.py` | Sync client tests (MagicMock transport) |
| 7 | `tests/test_async_clients/test_appdb.py` | Async client tests (respx) |

### Models (`src/domo_sdk/models/appdb.py`)

```python
"""AppDB (document store) models."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel
from domo_sdk.models.datasets import ColumnType  # Reuse — identical enum


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
```

#### Research Insights: Models

**Changes from original plan (with rationale):**

| Change | Why |
|--------|-----|
| Reuse `ColumnType` from `models.datasets` | Identical 6-value enum — no duplication. Import is one line. |
| Removed `EntityType` and `Permission` enums | They were defined but never used in method signatures (dead code). If needed later, add when a method actually uses them. |
| `content: dict[str, Any] = Field(default_factory=dict)` | Mutable default (`{}`) is a Pydantic footgun — instances can share the same dict object. `default_factory` creates a new dict per instance. |
| `columns: list[SchemaColumn] = Field(default_factory=list)` | Same mutable default issue with `[]`. |
| `owner: int` on both models (was `str` on `AppDBDocument`) | API returns numeric user IDs for both collections and documents. Consistent typing. Verify against live API response during implementation. |
| `created_by: int` / `updated_by: int` on `AppDBDocument` | Same — numeric IDs, not string. |

**Security note:** All fields have safe defaults. `extra="ignore"` from `DomoModel` base handles unknown API fields gracefully.

### Sync Client (`src/domo_sdk/clients/appdb.py`)

```python
"""AppDB client for the Domo API."""
from __future__ import annotations

import json
from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.appdb import (
    AppDBCollection,
    AppDBDocument,
    BulkOperationResult,
)

# Determined by pre-implementation URL validation step
URL_BASE = "/datastores/v1/collections"
URL_BASE_V2 = "/datastores/v2/collections"

# Aggregation keys accepted by the v2 query endpoint
_QUERY_AGGREGATION_KEYS = frozenset({"groupby", "count", "avg", "min", "max", "sum"})


class AppDBClient(DomoAPIClient):
    """Manage AppDB collections and documents.

    AppDB is Domo's NoSQL document store for custom apps.
    Requires Developer Token authentication.

    Docs: https://developer.domo.com/docs/appdb-api-reference
    """

    # --- Collection operations ---

    def create_collection(
        self,
        name: str,
        schema: dict[str, Any] | None = None,
        sync_enabled: bool = False,
    ) -> AppDBCollection:
        """Create a new collection."""
        body: dict[str, Any] = {"name": name, "syncEnabled": sync_enabled}
        if schema:
            body["schema"] = schema
        result = self._create(URL_BASE, body)
        return AppDBCollection.model_validate(result)

    def get_collection(self, collection_id: str) -> AppDBCollection:
        """Get a collection by name or ID."""
        result = self._get(f"{URL_BASE}/{collection_id}")
        return AppDBCollection.model_validate(result)

    def list_collections(self) -> list[AppDBCollection]:
        """List all collections."""
        result = self._list(URL_BASE)
        return [AppDBCollection.model_validate(c) for c in result]

    def update_collection(
        self,
        collection_id: str,
        update_data: dict[str, Any],
    ) -> AppDBCollection:
        """Update a collection (schema, sync settings)."""
        result = self._update(f"{URL_BASE}/{collection_id}", update_data)
        return AppDBCollection.model_validate(result)

    def delete_collection(self, collection_id: str) -> None:
        """Delete a collection and all its documents."""
        self._delete(f"{URL_BASE}/{collection_id}")

    # --- Document operations ---

    def create_document(
        self,
        collection_id: str,
        content: dict[str, Any],
    ) -> AppDBDocument:
        """Create a document in a collection."""
        result = self._create(
            f"{URL_BASE}/{collection_id}/documents",
            {"content": content},
        )
        return AppDBDocument.model_validate(result)

    def get_document(
        self,
        collection_id: str,
        document_id: str,
    ) -> AppDBDocument:
        """Get a document by ID."""
        result = self._get(
            f"{URL_BASE}/{collection_id}/documents/{document_id}"
        )
        return AppDBDocument.model_validate(result)

    def list_documents(self, collection_id: str) -> list[AppDBDocument]:
        """List all documents in a collection.

        Note: Hard limit of 10,000 documents. For larger collections,
        use query() with limit/offset for pagination.
        """
        result = self._list(f"{URL_BASE}/{collection_id}/documents")
        return [AppDBDocument.model_validate(d) for d in result]

    def update_document(
        self,
        collection_id: str,
        document_id: str,
        content: dict[str, Any],
    ) -> AppDBDocument:
        """Replace a document's content."""
        result = self._update(
            f"{URL_BASE}/{collection_id}/documents/{document_id}",
            {"content": content},
        )
        return AppDBDocument.model_validate(result)

    def delete_document(
        self,
        collection_id: str,
        document_id: str,
    ) -> None:
        """Delete a document."""
        self._delete(
            f"{URL_BASE}/{collection_id}/documents/{document_id}"
        )

    # --- Query ---

    def query(
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

        result = self.transport.post(
            f"{URL_BASE_V2}/{collection_id}/documents/query",
            body=query,
            params=params,
        )
        return [AppDBDocument.model_validate(d) for d in result]

    # --- Bulk operations ---

    def bulk_create(
        self,
        collection_id: str,
        documents: list[dict[str, Any]],
    ) -> BulkOperationResult:
        """Create multiple documents at once."""
        body = [{"content": doc} for doc in documents]
        result = self._create(
            f"{URL_BASE}/{collection_id}/documents/bulk", body
        )
        return BulkOperationResult.model_validate(result)

    def bulk_upsert(
        self,
        collection_id: str,
        documents: list[dict[str, Any]],
    ) -> BulkOperationResult:
        """Create or update multiple documents.

        Documents with an 'id' key are updated; those without are created.
        """
        result = self._update(
            f"{URL_BASE}/{collection_id}/documents/bulk", documents
        )
        return BulkOperationResult.model_validate(result)

    def bulk_delete(
        self,
        collection_id: str,
        document_ids: list[str],
    ) -> BulkOperationResult:
        """Delete multiple documents by ID.

        Note: IDs are passed as query params. For very large lists
        (500+ UUIDs), batch your calls to avoid URL length limits.

        Requires prerequisite transport PR (delete with params + return body).
        """
        ids_str = ",".join(document_ids)
        result = self._delete(
            f"{URL_BASE}/{collection_id}/documents/bulk",
            params={"ids": ids_str},
        )
        return BulkOperationResult.model_validate(result)

    # --- Partial update ---

    def partial_update(
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
        result = self._update(
            f"{URL_BASE}/{collection_id}/documents/update", body
        )
        return BulkOperationResult.model_validate(result)

    # --- Permissions ---

    def set_permission(
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

        Requires prerequisite transport PR (put with params).
        """
        url = (
            f"{URL_BASE}/{collection_id}"
            f"/permission/{entity_type}/{entity_id}"
        )
        self._update(
            url,
            body=None,
            params={"permissions": ",".join(permissions)},
        )

    def remove_permission(
        self,
        collection_id: str,
        entity_type: str,
        entity_id: str,
    ) -> None:
        """Remove all permissions for an entity on a collection."""
        self._delete(
            f"{URL_BASE}/{collection_id}"
            f"/permission/{entity_type}/{entity_id}"
        )

    # --- Export ---

    def export(self) -> None:
        """Trigger a manual export of all AppDB data to datasets.

        Raises DomoAPIError with status 423 if an export is already
        in progress.
        """
        self._create("/datastores/v1/export", body=None)
```

#### Research Insights: Client

**Changes from original plan (with rationale):**

| Change | Why |
|--------|-----|
| `import json` at module top | Inline import was a style violation — module-level is standard. |
| `URL_BASE_V2` constant | v2 URL was hardcoded inline in `query()`. Extract for consistency. |
| Explicit query params instead of `**aggregation` | `**kwargs` with underscore-to-camelCase magic is undiscoverable. IDE can't autocomplete `group_by=`, `count=`, etc. Explicit keyword-only params are clearer. |
| `query()` uses keyword-only args (`*`) | Prevents positional arg mistakes — `query(col, q, 100)` is ambiguous. |
| `partial_update` returns `BulkOperationResult` | Original returned `dict` — violates the "all methods return models" criterion. The API returns Created/Updated/Deleted counts. |
| `set_permission` sends `permissions` via `params` | Original accepted `permissions` param but never sent it (dead code). Now passes via query params on PUT. Requires transport prerequisite. |
| `export()` returns `None` | Original returned `dict` but the API returns 200 with no meaningful body. Void is clearer. Routes through `_create` for POST semantics. |
| `bulk_delete` uses `_delete` with `params` | Requires transport prerequisite. After prerequisite PR, `_delete` accepts `params` and returns response body. |
| Docstring warns about empty query in `partial_update` | Empty `{}` query matches all documents — destructive if misused. |
| `update_data: dict[str, Any]` (typed) | Bare `dict` replaced with `dict[str, Any]` throughout. |

**Security considerations:**
- Path parameters (`collection_id`, `document_id`, `entity_type`, `entity_id`) are passed directly to URL construction. The transport layer URL-encodes via `requests`/`httpx`, but malicious input like `../../other` could be concerning. For v1, this is acceptable — Domo's server validates these. Add regex validation if needed later.
- `partial_update` with empty query `{}` matches ALL documents. Docstring warns about this. Not adding a runtime check (YAGNI) — the Domo API itself accepts it.

**Performance considerations:**
- `list_documents` hard limit is 10K docs. For large collections, `query()` with `limit`/`offset` is the pagination mechanism. Documenting this in the docstring.
- At 10K documents, `[model_validate(d) for d in result]` creates 10K model instances. If profiling shows this is a bottleneck, swap to `TypeAdapter(list[AppDBDocument]).validate_python(result)` for batch validation.
- `bulk_create`/`bulk_upsert` have API-side limits. Document the 500+ UUID threshold for `bulk_delete` URL length.

### Async Client (`src/domo_sdk/async_clients/appdb.py`)

Mechanical mirror — same methods, `async def` + `await`, returns same models. Uses `AsyncDomoAPIClient` base. List methods return `list[Model]` (not generators).

Key difference: `bulk_delete` uses `await self._delete(url, params=...)` — same prerequisite applies to `AsyncTransport.delete()`.

### Wiring (`src/domo_sdk/domo.py`)

Two changes:

```python
# At top — add imports:
from domo_sdk.clients.appdb import AppDBClient
from domo_sdk.async_clients.appdb import AsyncAppDBClient

# In Domo._init_clients():
self.appdb = AppDBClient(self.transport)

# In AsyncDomo._init_clients():
self.appdb = AsyncAppDBClient(self.transport)
```

### Test Patterns

**Model tests** — standard Pydantic validation, same as existing:

```python
class TestAppDBDocument:
    def test_document_from_api_response(self) -> None:
        data = {
            "id": "abc-123",
            "datastoreId": "ds-456",
            "collectionId": "col-789",
            "content": {"name": "Widget", "price": 9.99},
            "owner": 12345,
            "createdBy": 12345,
            "createdOn": "2024-05-08T19:39:00.708Z",
        }
        doc = AppDBDocument.model_validate(data)
        assert doc.id == "abc-123"
        assert doc.content["name"] == "Widget"
        assert doc.collection_id == "col-789"  # alias works

    def test_mutable_defaults_are_independent(self) -> None:
        """Verify Field(default_factory=...) creates independent instances."""
        doc1 = AppDBDocument()
        doc2 = AppDBDocument()
        doc1.content["key"] = "value"
        assert "key" not in doc2.content
```

**Sync client tests** — mock transport returns dict, assert client returns model:

```python
def test_get_document(self) -> None:
    client, transport = _make_client()
    transport.get.return_value = {
        "id": "doc-1", "content": {"key": "value"},
        "datastoreId": "ds", "collectionId": "col",
        "owner": 12345,
    }

    result = client.get_document("my-collection", "doc-1")

    transport.get.assert_called_once_with(
        "/datastores/v1/collections/my-collection/documents/doc-1",
        params=None,
    )
    assert isinstance(result, AppDBDocument)
    assert result.id == "doc-1"
    assert result.content == {"key": "value"}

def test_query_with_aggregation(self) -> None:
    """Verify explicit aggregation params are forwarded correctly."""
    client, transport = _make_client()
    transport.post.return_value = []

    client.query(
        "my-collection",
        {"content.status": {"$eq": "active"}},
        limit=10,
        group_by="content.category",
        count="content.id",
    )

    transport.post.assert_called_once_with(
        "/datastores/v2/collections/my-collection/documents/query",
        body={"content.status": {"$eq": "active"}},
        params={"limit": 10, "groupby": "content.category", "count": "content.id"},
    )

def test_set_permission_sends_permissions(self) -> None:
    """Verify permissions are actually sent as query params."""
    client, transport = _make_client()
    transport.put.return_value = None

    client.set_permission("col-1", "USER", "123", ["read", "write"])

    transport.put.assert_called_once_with(
        "/datastores/v1/collections/col-1/permission/USER/123",
        body=None,
        params={"permissions": "read,write"},
    )
```

## Acceptance Criteria

### Functional Requirements

- [x] Collection CRUD: create, get, list, update, delete
- [x] Document CRUD: create, get, list, update, delete
- [x] MongoDB-style query with pagination params (limit, offset, order_by)
- [x] Query aggregation with explicit keyword params (group_by, count, avg, min, max, sum)
- [x] Bulk operations: create, upsert, delete
- [x] Partial update with MongoDB operators ($set, $unset, $inc, etc.)
- [x] Permission management: set (with permissions list), remove
- [x] Export trigger
- [x] All methods return Pydantic models (except void methods)
- [x] Both sync and async clients

### Non-Functional Requirements

- [x] Prerequisite transport PR merged (params on put/delete, delete returns body)
- [ ] URL_BASE validated against live Domo instance before implementation
- [x] All sync client methods have MagicMock transport tests
- [x] All async client methods have respx-based tests
- [x] All models have validation + defaults + serialization tests
- [x] Mutable default test (verify `default_factory` independence)
- [x] `ruff check` and `mypy` pass
- [x] Docstrings note "Requires Developer Token authentication" on client class
- [x] No `ColumnType` duplication — reuses `models.datasets.ColumnType`

### Quality Gates

- [x] `pytest` passes with no failures
- [x] New pattern (model returns) is clean enough to copy for next client
- [x] No changes to existing clients (transport prerequisite is separate PR)
- [x] `set_permission` test verifies permissions are actually sent
- [x] `partial_update` returns `BulkOperationResult`, not `dict`

## Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| **BLOCKING: Transport params gap** | Ship prerequisite PR first — 4 files, backward-compatible, small review |
| URL path incorrect for transport routing | Pre-validate with curl before writing any code |
| `owner` type (int vs str) uncertain | Verify against live API response. Plan assumes `int` based on collection pattern. |
| `partial_update` requires JSON-stringified body fields | Use `json.dumps()` — unusual but matches API |
| 423 LOCKED on export not handled by transport | Falls through to `DomoAPIError` — acceptable for v1, add specific handling later |
| `bulk_delete` URL length limits | Document the limit, don't auto-chunk in v1 |
| `ColumnType` import coupling | AppDB models now depend on `models.datasets`. Acceptable — same SDK package, identical enum. If datasets model ever diverges, extract to `models.common`. |

## Implementation Order

```
1. [PR] Transport params: put()/delete() params + delete() return body (4 files)
   ↓
2. [PR] AppDB client (7 files, depends on #1)
   a. models/appdb.py — models first, testable independently
   b. clients/appdb.py — sync client
   c. async_clients/appdb.py — async mirror
   d. domo.py — wire up
   e. tests/ — all three test files
```

## References

### Internal References

- Brainstorm: `docs/brainstorms/2026-03-03-expand-api-coverage-brainstorm.md`
- Reference client: `src/domo_sdk/clients/roles.py`
- Reference model: `src/domo_sdk/models/roles.py`
- Reference test: `tests/test_clients/test_roles.py`
- Transport routing: `src/domo_sdk/transport/auth.py:189-193`
- Base client class: `src/domo_sdk/clients/base.py`
- ColumnType source: `src/domo_sdk/models/datasets.py:14-20`
- Transport gaps: `src/domo_sdk/transport/sync_transport.py:118,152`

### External References

- [Domo AppDB API Documentation](https://developer.domo.com/docs/appdb-api-reference)
- [Domo AppDB OpenAPI Spec](https://github.com/DomoApps/domo-documentation-hub/blob/main/openapi/product/appdb.yaml)
- [signalv/domoappdb TypeScript Library](https://github.com/signalv/domoappdb) — community reference for undocumented endpoints
- [AppDB Bulk Limits Discussion](https://community-forums.domo.com/main/discussion/66156/appdb-api-bulk-document-request-size-and-rate-limits)
