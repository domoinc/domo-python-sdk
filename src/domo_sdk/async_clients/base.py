"""Base client for asynchronous API clients."""

from __future__ import annotations

import logging
from typing import Any

from domo_sdk.transport.async_transport import AsyncTransport

logger = logging.getLogger("domo_sdk.async_clients")


class AsyncDomoAPIClient:
    """Base class for all asynchronous API clients.

    Provides async CRUD helper methods with centralized error handling.
    """

    def __init__(self, transport: AsyncTransport, logger_: logging.Logger | None = None) -> None:
        self.transport = transport
        self.logger = logger_ or logger

    async def _create(self, url: str, body: Any, params: dict[str, Any] | None = None) -> Any:
        return await self.transport.post(url, body=body, params=params)

    async def _get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        return await self.transport.get(url, params=params)

    async def _list(self, url: str, params: dict[str, Any] | None = None) -> Any:
        return await self.transport.get(url, params=params)

    async def _update(self, url: str, body: Any, method: str = "PUT", params: dict[str, Any] | None = None) -> Any:
        if method == "PATCH":
            return await self.transport.patch(url, body=body)
        return await self.transport.put(url, body=body, params=params)

    async def _delete(self, url: str, params: dict[str, Any] | None = None) -> Any:
        return await self.transport.delete(url, params=params)

    async def _upload_csv(self, url: str, csv_data: bytes | str) -> Any:
        return await self.transport.put_csv(url, body=csv_data)

    async def _upload_gzip(self, url: str, data: bytes) -> Any:
        return await self.transport.put_gzip(url, body=data)

    async def _download_csv(self, url: str, include_header: bool = True) -> str:
        return await self.transport.get_csv(url, params={"includeHeader": str(include_header)})
