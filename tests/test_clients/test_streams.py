"""Tests for StreamClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.streams import StreamClient
from domo_sdk.models.streams import Stream, StreamExecution


def _make_client() -> tuple[StreamClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return StreamClient(transport), transport


class TestStreamCRUD:
    """Stream CRUD tests."""

    def test_create(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 1,
            "dataSet": {"id": "ds-1"},
            "updateMethod": "REPLACE",
        }

        result = client.create(
            {"dataSet": {"id": "ds-1"}, "updateMethod": "REPLACE"}
        )

        assert isinstance(result, Stream)
        assert result.id == 1

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 42,
            "dataSet": {"id": "ds-1"},
            "updateMethod": "APPEND",
        }

        result = client.get(42)

        assert isinstance(result, Stream)
        assert result.id == 42

    def test_list_pagination(self) -> None:
        client, transport = _make_client()
        transport.get.side_effect = [
            [{"id": 1}, {"id": 2}],
            [{"id": 3}],
            [],
        ]

        results = list(client.list(per_page=2))

        assert len(results) == 3
        assert all(isinstance(s, Stream) for s in results)

    def test_search(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [{"id": 1}, {"id": 2}]

        results = client.search("sales")

        transport.get.assert_called_once_with(
            "/v1/streams/search", params={"q": "sales"}
        )
        assert len(results) == 2
        assert all(isinstance(s, Stream) for s in results)

    def test_update(self) -> None:
        client, transport = _make_client()
        transport.patch.return_value = {
            "id": 1,
            "updateMethod": "APPEND",
        }

        result = client.update(1, {"updateMethod": "APPEND"})

        assert isinstance(result, Stream)

    def test_delete(self) -> None:
        client, transport = _make_client()

        client.delete(1)

        transport.delete.assert_called_once_with(
            "/v1/streams/1", params=None
        )


class TestStreamExecutions:
    """Stream execution tests."""

    def test_create_execution(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 100,
            "currentState": "ACTIVE",
        }

        result = client.create_execution(1)

        assert isinstance(result, StreamExecution)
        assert result.id == 100
        assert result.current_state == "ACTIVE"

    def test_get_execution(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 100,
            "currentState": "ACTIVE",
            "rows": 500,
        }

        result = client.get_execution(1, 100)

        assert isinstance(result, StreamExecution)
        assert result.rows == 500

    def test_list_executions(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 100, "currentState": "ACTIVE"},
            {"id": 101, "currentState": "SUCCEEDED"},
        ]

        results = client.list_executions(1)

        assert len(results) == 2
        assert all(isinstance(e, StreamExecution) for e in results)

    def test_upload_part(self) -> None:
        client, transport = _make_client()

        client.upload_part(1, 100, 1, "col1,col2\na,b\n")

        transport.put_csv.assert_called_once()
        call_url = transport.put_csv.call_args[0][0]
        assert "/executions/100/part/1" in call_url

    def test_commit_execution(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {
            "id": 100,
            "currentState": "SUCCEEDED",
        }

        result = client.commit_execution(1, 100)

        assert isinstance(result, StreamExecution)
        assert result.current_state == "SUCCEEDED"

    def test_abort_execution(self) -> None:
        client, transport = _make_client()

        client.abort_execution(1, 100)

        transport.put.assert_called_once()
        call_url = transport.put.call_args[0][0]
        assert "/executions/100/abort" in call_url
