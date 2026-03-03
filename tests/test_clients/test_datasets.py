"""Tests for DataSetClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.datasets import DataSetClient


def _make_client() -> tuple[DataSetClient, MagicMock]:
    """Create a DataSetClient with a fully mocked transport."""
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    client = DataSetClient(transport)
    return client, transport


class TestDataSetClientCRUD:
    """Tests for DataSet CRUD operations."""

    def test_create_dataset(self) -> None:
        """POST to /v1/datasets."""
        client, transport = _make_client()
        transport.post.return_value = {"id": "new-ds", "name": "Test"}

        body = {"name": "Test", "schema": {"columns": [{"type": "STRING", "name": "col1"}]}}
        result = client.create(body)

        transport.post.assert_called_once_with("/v1/datasets", body=body, params=None)
        assert result["id"] == "new-ds"

    def test_get_dataset(self) -> None:
        """GET to /v1/datasets/{id}."""
        client, transport = _make_client()
        transport.get.return_value = {"id": "ds-123", "name": "Sales"}

        result = client.get("ds-123")

        transport.get.assert_called_once_with("/v1/datasets/ds-123", params=None)
        assert result["id"] == "ds-123"

    def test_list_datasets_pagination(self) -> None:
        """Pagination through multiple pages of datasets."""
        client, transport = _make_client()

        # First page returns 2 items, second page returns 1, third returns empty
        page1 = [{"id": "ds-1"}, {"id": "ds-2"}]
        page2 = [{"id": "ds-3"}]
        page3: list = []
        transport.get.side_effect = [page1, page2, page3]

        results = list(client.list(per_page=2))

        assert len(results) == 3
        assert results[0]["id"] == "ds-1"
        assert results[2]["id"] == "ds-3"
        assert transport.get.call_count == 3

    def test_list_datasets_with_limit(self) -> None:
        """Pagination stops after reaching the limit."""
        client, transport = _make_client()

        page1 = [{"id": "ds-1"}, {"id": "ds-2"}]
        transport.get.side_effect = [page1]

        results = list(client.list(per_page=2, limit=2))

        assert len(results) == 2

    def test_delete_dataset(self) -> None:
        """DELETE to /v1/datasets/{id}."""
        client, transport = _make_client()

        client.delete("ds-123")

        transport.delete.assert_called_once_with("/v1/datasets/ds-123", params=None)


class TestDataSetClientQuery:
    """Tests for DataSet query operations."""

    def test_query_dataset(self) -> None:
        """POST to /v1/datasets/query/execute/{id}."""
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
        assert result["numRows"] == 1


class TestDataSetClientMetadata:
    """Tests for DataSet metadata and schema operations."""

    def test_get_metadata(self) -> None:
        """GET to /data/v3/datasources/{id}?part=core."""
        client, transport = _make_client()
        transport.get.return_value = {"id": "ds-123", "name": "Sales"}

        result = client.get_metadata("ds-123")

        transport.get.assert_called_once_with(
            "/data/v3/datasources/ds-123",
            params={"part": "core"},
        )
        assert result["id"] == "ds-123"

    def test_get_schema(self) -> None:
        """GET to /data/v2/datasources/{id}/schemas/latest."""
        client, transport = _make_client()
        transport.get.return_value = {"columns": [{"type": "STRING", "name": "col1"}]}

        result = client.get_schema("ds-123")

        transport.get.assert_called_once_with(
            "/data/v2/datasources/ds-123/schemas/latest",
            params=None,
        )
        assert len(result["columns"]) == 1


class TestDataSetClientPDP:
    """Tests for PDP operations."""

    def test_create_pdp(self) -> None:
        """POST to /v1/datasets/{id}/policies."""
        client, transport = _make_client()
        transport.post.return_value = {"id": 1, "name": "My Policy"}

        pdp_request = {
            "name": "My Policy",
            "filters": [{"column": "region", "values": ["US"], "operator": "EQUALS", "not": False}],
            "users": [42],
        }
        result = client.create_pdp("ds-123", pdp_request)

        transport.post.assert_called_once_with(
            "/v1/datasets/ds-123/policies",
            body=pdp_request,
            params=None,
        )
        assert result["name"] == "My Policy"


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
