"""Dataflows client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.dataflows import Dataflow, DataflowExecution

URL_BASE = "/v1/dataflows"


class DataflowsClient(DomoAPIClient):
    """Manage Domo dataflows (ETL/Magic ETL).

    Docs: https://developer.domo.com/docs/dataflows-api-reference/dataflows
    """

    def list(
        self, per_page: int = 50, offset: int = 0
    ) -> list[Dataflow]:
        """List dataflows."""
        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        data = self._list(URL_BASE, params=params)
        return [Dataflow.model_validate(d) for d in data]

    def get(self, dataflow_id: int) -> Dataflow:
        """Retrieve a single dataflow by ID."""
        data = self._get(f"{URL_BASE}/{dataflow_id}")
        return Dataflow.model_validate(data)

    def execute(self, dataflow_id: int) -> DataflowExecution:
        """Execute a dataflow."""
        data = self._create(
            f"{URL_BASE}/{dataflow_id}/executions", None
        )
        return DataflowExecution.model_validate(data)

    def get_execution(
        self, dataflow_id: int, execution_id: int
    ) -> DataflowExecution:
        """Retrieve a specific execution for a dataflow."""
        data = self._get(
            f"{URL_BASE}/{dataflow_id}/executions/{execution_id}"
        )
        return DataflowExecution.model_validate(data)
