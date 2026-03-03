"""Async Dataflows client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.dataflows import Dataflow, DataflowExecution

URL_BASE = "/v1/dataflows"


class AsyncDataflowsClient(AsyncDomoAPIClient):
    """Manage Domo dataflows asynchronously.

    Docs: https://developer.domo.com/docs/dataflows-api-reference/dataflows
    """

    async def list(
        self,
        per_page: int = 50,
        offset: int = 0,
        limit: int = 0,
    ) -> list[Dataflow]:
        """Return a full list of dataflows, paginating internally."""
        if per_page not in range(1, 51):
            raise ValueError(
                "per_page must be between 1 and 50 (inclusive)"
            )

        if limit:
            per_page = min(per_page, limit)

        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        result: list[Dataflow] = []
        dataflows: list[dict] = await self._list(
            URL_BASE, params=params
        )

        while dataflows:
            for dataflow in dataflows:
                result.append(Dataflow.model_validate(dataflow))
                if limit and len(result) >= limit:
                    return result

            params["offset"] += per_page
            if limit and params["offset"] + per_page > limit:
                params["limit"] = limit - params["offset"]
            dataflows = await self._list(URL_BASE, params=params)

        return result

    async def get(self, dataflow_id: int) -> Dataflow:
        """Retrieve a single dataflow by ID."""
        data = await self._get(f"{URL_BASE}/{dataflow_id}")
        return Dataflow.model_validate(data)

    async def execute(
        self, dataflow_id: int
    ) -> DataflowExecution:
        """Start a dataflow execution."""
        url = f"{URL_BASE}/{dataflow_id}/executions"
        data = await self._create(url, {})
        return DataflowExecution.model_validate(data)

    async def get_execution(
        self, dataflow_id: int, execution_id: int
    ) -> DataflowExecution:
        """Get the status of a dataflow execution."""
        url = f"{URL_BASE}/{dataflow_id}/executions/{execution_id}"
        data = await self._get(url)
        return DataflowExecution.model_validate(data)
