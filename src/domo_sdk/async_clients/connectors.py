"""Async Connectors client for the Domo API."""

from __future__ import annotations

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.streams import StreamExecution

URL_BASE = "/v1/streams"


class AsyncConnectorsClient(AsyncDomoAPIClient):
    """Trigger Domo connector runs asynchronously.

    Uses the Streams API execution endpoint to initiate connector runs.
    """

    async def run(self, stream_id: int) -> StreamExecution:
        """Trigger a connector run via the Streams execution API."""
        url = f"{URL_BASE}/{stream_id}/executions"
        data = await self._create(url, {})
        return StreamExecution.model_validate(data)
