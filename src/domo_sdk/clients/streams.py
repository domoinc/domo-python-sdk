"""Stream client for the Domo API."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.streams import Stream, StreamExecution

URL_BASE = "/v1/streams"


class StreamClient(DomoAPIClient):
    """Manage Domo Streams.

    Use Streams when data is massive, constantly changing, or rapidly growing.

    Docs: https://developer.domo.com/docs/streams-api-reference/streams-2
    """

    def create(self, stream_request: dict) -> Stream:
        """Create a new stream."""
        data = self._create(URL_BASE, stream_request)
        return Stream.model_validate(data)

    def get(self, stream_id: int) -> Stream:
        """Retrieve a single stream by ID."""
        data = self._get(f"{URL_BASE}/{stream_id}")
        return Stream.model_validate(data)

    def list(
        self,
        per_page: int = 50,
        offset: int = 0,
        limit: int = 0,
    ) -> Generator[Stream, None, None]:
        """Paginating generator over streams."""
        if per_page not in range(1, 51):
            raise ValueError(
                "per_page must be between 1 and 50 (inclusive)"
            )

        if limit:
            per_page = min(per_page, limit)

        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        stream_count = 0
        streams: list[dict] = self._list(URL_BASE, params=params)

        while streams:
            for stream in streams:
                yield Stream.model_validate(stream)
                stream_count += 1
                if limit and stream_count >= limit:
                    return

            params["offset"] += per_page
            if limit and params["offset"] + per_page > limit:
                params["limit"] = limit - params["offset"]
            streams = self._list(URL_BASE, params=params)

    def search(self, query: str) -> list[Stream]:
        """Search streams by dataset name or ID."""
        data = self._list(f"{URL_BASE}/search", params={"q": query})
        return [Stream.model_validate(s) for s in data]

    def update(self, stream_id: int, stream_update: dict) -> Stream:
        """Update an existing stream."""
        data = self._update(
            f"{URL_BASE}/{stream_id}", stream_update, method="PATCH"
        )
        return Stream.model_validate(data)

    def delete(self, stream_id: int) -> None:
        """Delete a stream."""
        self._delete(f"{URL_BASE}/{stream_id}")

    def create_execution(self, stream_id: int) -> StreamExecution:
        """Create a new execution on a stream."""
        data = self._create(
            f"{URL_BASE}/{stream_id}/executions", None
        )
        return StreamExecution.model_validate(data)

    def get_execution(
        self, stream_id: int, execution_id: int
    ) -> StreamExecution:
        """Retrieve a specific execution."""
        url = f"{URL_BASE}/{stream_id}/executions/{execution_id}"
        data = self._get(url)
        return StreamExecution.model_validate(data)

    def list_executions(
        self,
        stream_id: int,
        per_page: int = 50,
        offset: int = 0,
    ) -> list[StreamExecution]:
        """List executions for a stream."""
        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        data = self._list(
            f"{URL_BASE}/{stream_id}/executions", params=params
        )
        return [StreamExecution.model_validate(e) for e in data]

    def upload_part(
        self,
        stream_id: int,
        execution_id: int,
        part_num: int,
        csv_data: str,
    ) -> None:
        """Upload a data part to a stream execution."""
        url = (
            f"{URL_BASE}/{stream_id}/executions"
            f"/{execution_id}/part/{part_num}"
        )
        self._upload_csv(url, csv_data)

    def commit_execution(
        self, stream_id: int, execution_id: int
    ) -> StreamExecution:
        """Commit a stream execution."""
        url = (
            f"{URL_BASE}/{stream_id}/executions/{execution_id}/commit"
        )
        data = self._update(url, None)
        return StreamExecution.model_validate(data)

    def abort_execution(
        self, stream_id: int, execution_id: int
    ) -> None:
        """Abort a stream execution."""
        url = (
            f"{URL_BASE}/{stream_id}/executions/{execution_id}/abort"
        )
        self._update(url, None)
