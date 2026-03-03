"""Async Stream client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.streams import Stream, StreamExecution

URL_BASE = "/v1/streams"


class AsyncStreamClient(AsyncDomoAPIClient):
    """Manage Domo Streams asynchronously.

    Use Streams for data sources that are massive, constantly changing,
    or rapidly growing.  For simpler cases, use DataSets instead.

    Docs: https://developer.domo.com/docs/streams-api-reference/streams
    """

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def create(self, stream_request: dict) -> Stream:
        """Create a new Stream."""
        data = await self._create(URL_BASE, stream_request)
        return Stream.model_validate(data)

    async def get(self, stream_id: int) -> Stream:
        """Retrieve a single Stream by ID."""
        data = await self._get(f"{URL_BASE}/{stream_id}")
        return Stream.model_validate(data)

    async def list(
        self,
        per_page: int = 50,
        offset: int = 0,
        limit: int = 0,
    ) -> list[Stream]:
        """Return a full list of Streams, paginating internally."""
        if per_page not in range(1, 51):
            raise ValueError(
                "per_page must be between 1 and 50 (inclusive)"
            )

        if limit:
            per_page = min(per_page, limit)

        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        result: list[Stream] = []
        streams: list[dict] = await self._list(URL_BASE, params=params)

        while streams:
            for stream in streams:
                result.append(Stream.model_validate(stream))
                if limit and len(result) >= limit:
                    return result

            params["offset"] += per_page
            if limit and params["offset"] + per_page > limit:
                params["limit"] = limit - params["offset"]
            streams = await self._list(URL_BASE, params=params)

        return result

    async def search(self, query: str) -> list[Stream]:
        """Search streams by dataset name or ID."""
        data = await self._list(
            f"{URL_BASE}/search", params={"q": query}
        )
        return [Stream.model_validate(s) for s in data]

    async def update(self, stream_id: int, stream_update: dict) -> Stream:
        """Update an existing Stream."""
        data = await self._update(
            f"{URL_BASE}/{stream_id}", stream_update, method="PATCH"
        )
        return Stream.model_validate(data)

    async def delete(self, stream_id: int) -> None:
        """Delete a Stream."""
        await self._delete(f"{URL_BASE}/{stream_id}")

    # ------------------------------------------------------------------
    # Executions
    # ------------------------------------------------------------------

    async def create_execution(
        self, stream_id: int
    ) -> StreamExecution:
        """Create a new execution for a Stream."""
        url = f"{URL_BASE}/{stream_id}/executions"
        data = await self._create(url, None)
        return StreamExecution.model_validate(data)

    async def get_execution(
        self, stream_id: int, execution_id: int
    ) -> StreamExecution:
        """Retrieve a specific execution."""
        url = f"{URL_BASE}/{stream_id}/executions/{execution_id}"
        data = await self._get(url)
        return StreamExecution.model_validate(data)

    async def list_executions(
        self,
        stream_id: int,
        per_page: int = 50,
        offset: int = 0,
    ) -> list[StreamExecution]:
        """List executions for a Stream."""
        url = f"{URL_BASE}/{stream_id}/executions"
        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        data = await self._list(url, params=params)
        return [StreamExecution.model_validate(e) for e in data]

    async def upload_part(
        self,
        stream_id: int,
        execution_id: int,
        part_num: int,
        csv_data: str,
    ) -> None:
        """Upload a data part for a Stream execution."""
        url = (
            f"{URL_BASE}/{stream_id}/executions"
            f"/{execution_id}/part/{part_num}"
        )
        await self._upload_csv(url, csv_data.encode("utf-8"))

    async def commit_execution(
        self, stream_id: int, execution_id: int
    ) -> StreamExecution:
        """Commit (finalize) a Stream execution."""
        url = (
            f"{URL_BASE}/{stream_id}/executions/{execution_id}/commit"
        )
        data = await self._update(url, None)
        return StreamExecution.model_validate(data)

    async def abort_execution(
        self, stream_id: int, execution_id: int
    ) -> None:
        """Abort a Stream execution."""
        url = (
            f"{URL_BASE}/{stream_id}/executions/{execution_id}/abort"
        )
        await self._update(url, None)
