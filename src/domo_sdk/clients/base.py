"""Base client for synchronous API clients."""

from __future__ import annotations

import logging
from typing import Any

from domo_sdk.transport.sync_transport import SyncTransport

logger = logging.getLogger("domo_sdk.clients")


class DomoAPIClient:
    """Base class for all synchronous API clients.

    Provides CRUD helper methods with centralized error handling.
    """

    def __init__(self, transport: SyncTransport, logger_: logging.Logger | None = None) -> None:
        self.transport = transport
        self.logger = logger_ or logger

    def _create(self, url: str, body: Any, params: dict[str, Any] | None = None) -> Any:
        return self.transport.post(url, body=body, params=params)

    def _get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        return self.transport.get(url, params=params)

    def _list(self, url: str, params: dict[str, Any] | None = None) -> Any:
        return self.transport.get(url, params=params)

    def _update(self, url: str, body: Any, method: str = "PUT", params: dict[str, Any] | None = None) -> Any:
        if method == "PATCH":
            return self.transport.patch(url, body=body)
        return self.transport.put(url, body=body, params=params)

    def _delete(self, url: str, params: dict[str, Any] | None = None) -> Any:
        return self.transport.delete(url, params=params)

    def _upload_csv(self, url: str, csv_data: bytes | str) -> Any:
        return self.transport.put_csv(url, body=csv_data)

    def _upload_gzip(self, url: str, data: bytes) -> Any:
        return self.transport.put_gzip(url, body=data)

    def _download_csv(self, url: str, include_header: bool = True) -> str:
        return self.transport.get_csv(url, params={"includeHeader": str(include_header)})
