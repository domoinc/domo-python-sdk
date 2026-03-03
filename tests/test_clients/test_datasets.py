"""Tests for DataSetClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.datasets import DataSetClient
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


def _make_client() -> tuple[DataSetClient, MagicMock]:
    """Create a DataSetClient with a fully mocked transport."""
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    client = DataSetClient(transport)
    return client, transport


# ------------------------------------------------------------------
# CRUD
# ------------------------------------------------------------------


class TestDataSetClientCRUD:
    """Tests for DataSet CRUD operations."""

    def test_create_dataset(self) -> None:
        """POST to /v1/datasets returns DataSet model."""
        client, transport = _make_client()
        transport.post.return_value = {"id": "new-ds", "name": "Test"}

        body = {
            "name": "Test",
            "schema": {"columns": [{"type": "STRING", "name": "col1"}]},
        }
        result = client.create(body)

        transport.post.assert_called_once_with(
            "/v1/datasets", body=body, params=None
        )
        assert isinstance(result, DataSet)
        assert result.id == "new-ds"
        assert result.name == "Test"

    def test_get_dataset(self) -> None:
        """GET to /v1/datasets/{id} returns DataSet model."""
        client, transport = _make_client()
        transport.get.return_value = {"id": "ds-123", "name": "Sales"}

        result = client.get("ds-123")

        transport.get.assert_called_once_with(
            "/v1/datasets/ds-123", params=None
        )
        assert isinstance(result, DataSet)
        assert result.id == "ds-123"
        assert result.name == "Sales"

    def test_list_datasets_pagination(self) -> None:
        """Pagination yields DataSet models."""
        client, transport = _make_client()

        page1 = [{"id": "ds-1", "name": "A"}, {"id": "ds-2", "name": "B"}]
        page2 = [{"id": "ds-3", "name": "C"}]
        page3: list = []
        transport.get.side_effect = [page1, page2, page3]

        results = list(client.list(per_page=2))

        assert len(results) == 3
        assert all(isinstance(r, DataSet) for r in results)
        assert results[0].id == "ds-1"
        assert results[2].id == "ds-3"
        assert transport.get.call_count == 3

    def test_list_datasets_with_limit(self) -> None:
        """Pagination stops after reaching the limit."""
        client, transport = _make_client()

        page1 = [{"id": "ds-1", "name": "A"}, {"id": "ds-2", "name": "B"}]
        transport.get.side_effect = [page1]

        results = list(client.list(per_page=2, limit=2))

        assert len(results) == 2
        assert all(isinstance(r, DataSet) for r in results)

    def test_update_dataset(self) -> None:
        """PUT to /v1/datasets/{id} returns DataSet model."""
        client, transport = _make_client()
        transport.put.return_value = {
            "id": "ds-123",
            "name": "Updated",
        }

        result = client.update("ds-123", {"name": "Updated"})

        assert isinstance(result, DataSet)
        assert result.name == "Updated"

    def test_delete_dataset(self) -> None:
        """DELETE to /v1/datasets/{id}."""
        client, transport = _make_client()

        client.delete("ds-123")

        transport.delete.assert_called_once_with(
            "/v1/datasets/ds-123", params=None
        )


# ------------------------------------------------------------------
# Query
# ------------------------------------------------------------------


class TestDataSetClientQuery:
    """Tests for DataSet query operations."""

    def test_query_dataset(self) -> None:
        """POST to /v1/datasets/query/execute/{id} returns QueryResult."""
        client, transport = _make_client()
        transport.post.return_value = {
            "columns": ["name"],
            "rows": [["Alice"]],
            "numRows": 1,
            "numColumns": 1,
        }

        result = client.query("ds-123", "SELECT name FROM table")

        transport.post.assert_called_once_with(
            "/v1/datasets/query/execute/ds-123",
            body={"sql": "SELECT name FROM table"},
            params=None,
        )
        assert isinstance(result, QueryResult)
        assert result.num_rows == 1
        assert result.columns == ["name"]
        assert result.rows == [["Alice"]]


# ------------------------------------------------------------------
# Schema & metadata
# ------------------------------------------------------------------


class TestDataSetClientMetadata:
    """Tests for DataSet metadata and schema operations."""

    def test_get_metadata(self) -> None:
        """GET /data/v3/datasources/{id}?part=core returns DataSet."""
        client, transport = _make_client()
        transport.get.return_value = {"id": "ds-123", "name": "Sales"}

        result = client.get_metadata("ds-123")

        transport.get.assert_called_once_with(
            "/data/v3/datasources/ds-123",
            params={"part": "core"},
        )
        assert isinstance(result, DataSet)
        assert result.id == "ds-123"

    def test_get_schema(self) -> None:
        """GET /data/v2/datasources/{id}/schemas/latest returns Schema."""
        client, transport = _make_client()
        transport.get.return_value = {
            "columns": [{"type": "STRING", "name": "col1"}]
        }

        result = client.get_schema("ds-123")

        transport.get.assert_called_once_with(
            "/data/v2/datasources/ds-123/schemas/latest",
            params=None,
        )
        assert isinstance(result, Schema)
        assert len(result.columns) == 1
        assert result.columns[0].name == "col1"

    def test_alter_schema(self) -> None:
        """POST /data/v2/datasources/{id}/schemas returns Schema."""
        client, transport = _make_client()
        transport.post.return_value = {
            "columns": [
                {"type": "STRING", "name": "col1"},
                {"type": "LONG", "name": "col2"},
            ]
        }

        schema = {
            "columns": [
                {"type": "STRING", "name": "col1"},
                {"type": "LONG", "name": "col2"},
            ]
        }
        result = client.alter_schema("ds-123", schema)

        assert isinstance(result, Schema)
        assert len(result.columns) == 2


# ------------------------------------------------------------------
# Permissions & sharing
# ------------------------------------------------------------------


class TestDataSetClientPermissions:
    """Tests for permission and sharing operations."""

    def test_get_permissions(self) -> None:
        """GET returns list of DataSetPermission models."""
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 42, "type": "USER", "permissions": ["READ"]},
            {"id": 99, "type": "GROUP", "permissions": ["READ", "WRITE"]},
        ]

        result = client.get_permissions("ds-123")

        assert len(result) == 2
        assert all(isinstance(p, DataSetPermission) for p in result)
        assert result[0].id == 42
        assert result[1].permissions == ["READ", "WRITE"]

    def test_share(self) -> None:
        """POST /data/v3/datasources/{id}/share sends correct body."""
        client, transport = _make_client()
        transport.post.return_value = None

        client.share(
            "ds-123",
            [{"id": 42, "type": "USER", "accessLevel": "READ"}],
            send_email=True,
        )

        transport.post.assert_called_once()
        call_body = transport.post.call_args[1]["body"]
        assert call_body["sendEmail"] is True
        assert len(call_body["permissions"]) == 1

    def test_revoke_access(self) -> None:
        """DELETE /data/v3/datasources/{id}/permissions/USER/{userId}."""
        client, transport = _make_client()

        client.revoke_access("ds-123", 42)

        transport.delete.assert_called_once_with(
            "/data/v3/datasources/ds-123/permissions/USER/42",
            params=None,
        )


# ------------------------------------------------------------------
# Tags
# ------------------------------------------------------------------


class TestDataSetClientTags:
    """Tests for tag operations."""

    def test_set_tags(self) -> None:
        """POST /data/ui/v3/datasources/{id}/tags."""
        client, transport = _make_client()
        transport.post.return_value = None

        client.set_tags("ds-123", ["sales", "q4"])

        transport.post.assert_called_once_with(
            "/data/ui/v3/datasources/ds-123/tags",
            body=["sales", "q4"],
            params=None,
        )


# ------------------------------------------------------------------
# PDP
# ------------------------------------------------------------------


class TestDataSetClientPDP:
    """Tests for PDP operations."""

    def test_create_pdp(self) -> None:
        """POST to /v1/datasets/{id}/policies returns Policy."""
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 1,
            "name": "My Policy",
            "type": "user",
        }

        pdp_request = {
            "name": "My Policy",
            "filters": [
                {
                    "column": "region",
                    "values": ["US"],
                    "operator": "EQUALS",
                    "not": False,
                }
            ],
            "users": [42],
        }
        result = client.create_pdp("ds-123", pdp_request)

        assert isinstance(result, Policy)
        assert result.name == "My Policy"

    def test_get_pdp(self) -> None:
        """GET /v1/datasets/{id}/policies/{policyId} returns Policy."""
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 1,
            "name": "P1",
            "type": "user",
        }

        result = client.get_pdp("ds-123", 1)

        assert isinstance(result, Policy)
        assert result.id == 1

    def test_list_pdps(self) -> None:
        """GET /v1/datasets/{id}/policies returns list of Policy."""
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "P1", "type": "user"},
            {"id": 2, "name": "P2", "type": "user"},
        ]

        result = client.list_pdps("ds-123")

        assert len(result) == 2
        assert all(isinstance(p, Policy) for p in result)

    def test_update_pdp(self) -> None:
        """PUT /v1/datasets/{id}/policies/{policyId} returns Policy."""
        client, transport = _make_client()
        transport.put.return_value = {
            "id": 1,
            "name": "Updated",
            "type": "user",
        }

        result = client.update_pdp("ds-123", 1, {"name": "Updated"})

        assert isinstance(result, Policy)
        assert result.name == "Updated"

    def test_delete_pdp(self) -> None:
        """DELETE /v1/datasets/{id}/policies/{policyId}."""
        client, transport = _make_client()

        client.delete_pdp("ds-123", 1)

        transport.delete.assert_called_once_with(
            "/v1/datasets/ds-123/policies/1",
            params=None,
        )


# ------------------------------------------------------------------
# Export
# ------------------------------------------------------------------


class TestDataSetClientExport:
    """Tests for data export."""

    def test_data_export(self) -> None:
        """CSV download via get_csv."""
        client, transport = _make_client()
        transport.get_csv.return_value = "name,age\nAlice,30\nBob,25\n"

        result = client.data_export("ds-123", include_csv_header=True)

        transport.get_csv.assert_called_once_with(
            "/v1/datasets/ds-123/data",
            params={"includeHeader": "True"},
        )
        assert "Alice" in result


# ------------------------------------------------------------------
# Versions & indexes
# ------------------------------------------------------------------


class TestDataSetClientVersions:
    """Tests for version and index operations."""

    def test_list_versions(self) -> None:
        """GET returns list of DataVersion models."""
        client, transport = _make_client()
        transport.get.return_value = [
            {"versionId": "v1", "rowCount": 100},
            {"versionId": "v2", "rowCount": 200},
        ]

        result = client.list_versions("ds-123")

        assert len(result) == 2
        assert all(isinstance(v, DataVersion) for v in result)
        assert result[0].version_id == "v1"
        assert result[1].row_count == 200

    def test_create_index(self) -> None:
        """POST returns Index model."""
        client, transport = _make_client()
        transport.post.return_value = {"columns": ["col1", "col2"]}

        result = client.create_index("ds-123", ["col1", "col2"])

        assert isinstance(result, Index)
        assert result.columns == ["col1", "col2"]


# ------------------------------------------------------------------
# Partitions
# ------------------------------------------------------------------


class TestDataSetClientPartitions:
    """Tests for partition operations."""

    def test_list_partitions(self) -> None:
        """GET returns list of Partition models."""
        client, transport = _make_client()
        transport.get.return_value = [
            {"partitionId": "2024-01", "name": "Jan 2024"},
            {"partitionId": "2024-02", "name": "Feb 2024"},
        ]

        result = client.list_partitions("ds-123")

        assert len(result) == 2
        assert all(isinstance(p, Partition) for p in result)
        assert result[0].partition_id == "2024-01"

    def test_delete_partition(self) -> None:
        """DELETE /api/query/v1/datasources/{id}/partition/{partitionId}."""
        client, transport = _make_client()

        client.delete_partition("ds-123", "2024-01")

        transport.delete.assert_called_once_with(
            "/api/query/v1/datasources/ds-123/partition/2024-01",
            params=None,
        )


# ------------------------------------------------------------------
# Upload sessions
# ------------------------------------------------------------------


class TestDataSetClientUploadSessions:
    """Tests for upload session operations."""

    def test_create_upload_session(self) -> None:
        """POST returns UploadSession model."""
        client, transport = _make_client()
        transport.post.return_value = {"uploadId": 42}

        result = client.create_upload_session("ds-123")

        transport.post.assert_called_once_with(
            "/data/v3/datasources/ds-123/uploads",
            body={"action": "REPLACE"},
            params=None,
        )
        assert isinstance(result, UploadSession)
        assert result.upload_id == 42

    def test_create_upload_session_with_partition(self) -> None:
        """POST passes partition tag as query param."""
        client, transport = _make_client()
        transport.post.return_value = {"uploadId": 99}

        result = client.create_upload_session(
            "ds-123", action="APPEND", partition_tag="2024-Q1"
        )

        transport.post.assert_called_once_with(
            "/data/v3/datasources/ds-123/uploads",
            body={"action": "APPEND"},
            params={"restateDataTag": "2024-Q1"},
        )
        assert result.upload_id == 99

    def test_upload_part(self) -> None:
        """PUT uploads CSV data part."""
        client, transport = _make_client()

        client.upload_part("ds-123", 42, 1, "col1,col2\na,b\n")

        transport.put_csv.assert_called_once()
        call_url = transport.put_csv.call_args[0][0]
        assert "/uploads/42/parts/1" in call_url

    def test_commit_upload(self) -> None:
        """PUT commits upload session."""
        client, transport = _make_client()

        client.commit_upload("ds-123", 42)

        transport.put.assert_called_once()
        call_url = transport.put.call_args[0][0]
        assert "/uploads/42/commit" in call_url
        call_body = transport.put.call_args[1]["body"]
        assert call_body["action"] == "REPLACE"
        assert call_body["index"] is True

    def test_commit_upload_with_partition(self) -> None:
        """PUT includes partition tag in body."""
        client, transport = _make_client()

        client.commit_upload(
            "ds-123", 42, action="APPEND", partition_tag="2024-Q1"
        )

        call_body = transport.put.call_args[1]["body"]
        assert call_body["restateDataTag"] == "2024-Q1"
        assert call_body["action"] == "APPEND"


# ------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------


class TestDataSetClientProperties:
    """Tests for property operations."""

    def test_set_properties(self) -> None:
        """PUT /data/v3/datasources/{id}/properties."""
        client, transport = _make_client()

        client.set_properties("ds-123", {"dataProviderType": "custom"})

        transport.put.assert_called_once()
        call_body = transport.put.call_args[1]["body"]
        assert call_body["dataProviderType"] == "custom"
