"""Asynchronous transport using httpx library."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from domo_sdk.exceptions import (
    DomoAPIError,
    DomoAuthError,
    DomoConnectionError,
    DomoNotFoundError,
    DomoRateLimitError,
    DomoTimeoutError,
)
from domo_sdk.transport.auth import AuthStrategy

logger = logging.getLogger("domo_sdk.transport.async")

DEFAULT_TIMEOUT = 60.0
CONNECT_TIMEOUT = 10.0
SLOW_REQUEST_THRESHOLD = 5.0
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB


class AsyncTransport:
    """Asynchronous HTTP transport wrapping httpx.AsyncClient.

    Uses connection pooling and supports context manager protocol
    for resource cleanup.
    """

    def __init__(
        self,
        auth: AuthStrategy,
        timeout: float = DEFAULT_TIMEOUT,
        connect_timeout: float = CONNECT_TIMEOUT,
    ) -> None:
        self._auth = auth
        self._timeout = httpx.Timeout(timeout=timeout, connect=connect_timeout)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def get_base_url(self) -> str:
        return self._auth.get_base_url()

    @property
    def auth_mode(self) -> str:
        return self._auth.auth_mode

    def _build_url(self, path: str) -> str:
        return self._auth.get_base_url() + path

    async def _get_headers(
        self, content_type: str | None = None, accept: str = "application/json"
    ) -> dict[str, str]:
        headers = await self._auth.get_headers_async()
        headers["Accept"] = accept
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _handle_response(self, response: httpx.Response, url: str) -> httpx.Response:
        status = response.status_code

        if status in (401, 403):
            raise DomoAuthError(f"Auth failed: {response.text}", status_code=status)
        elif status == 404:
            raise DomoNotFoundError(f"Not found: {url}")
        elif status == 429:
            retry_after = response.headers.get("Retry-After")
            raise DomoRateLimitError(
                retry_after=float(retry_after) if retry_after else None,
            )
        elif status >= 400:
            raise DomoAPIError(
                status_code=status,
                response_body=response.text,
            )

        # Check response size
        if len(response.content) > MAX_RESPONSE_SIZE:
            logger.error(f"Response too large: {len(response.content)} bytes exceeds {MAX_RESPONSE_SIZE}")
            raise DomoAPIError(message="Response too large", status_code=status)

        return response

    async def get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        headers = await self._get_headers()
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            response = await client.get(full_url, headers=headers, params=params or {})
            self._log_timing("GET", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    async def post(self, url: str, body: Any = None, params: dict[str, Any] | None = None) -> Any:
        headers = await self._get_headers(content_type="application/json")
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            response = await client.post(full_url, headers=headers, params=params or {}, json=body)
            self._log_timing("POST", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    async def put(self, url: str, body: Any = None, params: dict[str, Any] | None = None) -> Any:
        headers = await self._get_headers(content_type="application/json")
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            response = await client.put(full_url, headers=headers, params=params or {}, json=body)
            self._log_timing("PUT", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    async def patch(self, url: str, body: Any = None) -> Any:
        headers = await self._get_headers(content_type="application/json")
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            response = await client.patch(full_url, headers=headers, json=body)
            self._log_timing("PATCH", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    async def delete(self, url: str, params: dict[str, Any] | None = None) -> Any:
        headers = await self._get_headers()
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            response = await client.delete(full_url, headers=headers, params=params or {})
            self._log_timing("DELETE", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    async def put_csv(self, url: str, body: bytes | str) -> Any:
        headers = await self._get_headers(content_type="text/csv")
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            content = body if isinstance(body, bytes) else body.encode()
            response = await client.put(full_url, headers=headers, content=content)
            self._log_timing("PUT(csv)", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    async def put_gzip(self, url: str, body: bytes) -> Any:
        headers = await self._get_headers(content_type="text/csv")
        headers["Content-Encoding"] = "gzip"
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            response = await client.put(full_url, headers=headers, content=body)
            self._log_timing("PUT(gzip)", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    async def get_csv(self, url: str, params: dict[str, Any] | None = None) -> str:
        headers = await self._get_headers(accept="text/csv")
        full_url = self._build_url(url)
        client = await self._get_client()
        start = time.time()
        try:
            response = await client.get(full_url, headers=headers, params=params or {})
            self._log_timing("GET(csv)", url, time.time() - start)
            self._handle_response(response, url)
            return response.text
        except httpx.TimeoutException as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout.read or DEFAULT_TIMEOUT) from err
        except httpx.ConnectError as err:
            raise DomoConnectionError(url=url) from err

    def _log_timing(self, method: str, url: str, duration: float) -> None:
        if duration > SLOW_REQUEST_THRESHOLD:
            logger.warning(f"Slow request: {method} {url} took {duration:.2f}s")
        else:
            logger.debug(f"{method} {url} completed in {duration:.2f}s")
