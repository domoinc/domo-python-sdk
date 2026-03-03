"""Tests for DataflowsClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.dataflows import DataflowsClient
from domo_sdk.models.dataflows import Dataflow, DataflowExecution


def _make_client() -> tuple[DataflowsClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return DataflowsClient(transport), transport


class TestDataflowsCRUD:
    def test_list(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "ETL1"},
            {"id": 2, "name": "ETL2"},
        ]

        result = client.list()

        assert len(result) == 2
        assert all(isinstance(d, Dataflow) for d in result)

    def test_get(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 1,
            "name": "Sales ETL",
            "type": "ETL",
        }

        result = client.get(1)

        assert isinstance(result, Dataflow)
        assert result.name == "Sales ETL"


class TestDataflowsExecutions:
    def test_execute(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 10,
            "currentState": "ACTIVE",
        }

        result = client.execute(1)

        assert isinstance(result, DataflowExecution)
        assert result.current_state == "ACTIVE"

    def test_get_execution(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 10,
            "currentState": "SUCCEEDED",
        }

        result = client.get_execution(1, 10)

        assert isinstance(result, DataflowExecution)
        assert result.current_state == "SUCCEEDED"
