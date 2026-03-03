"""Synchronous transport using requests library."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests
from requests_toolbelt.utils import dump

from domo_sdk.exceptions import (
    DomoAPIError,
    DomoAuthError,
    DomoConnectionError,
    DomoNotFoundError,
    DomoRateLimitError,
    DomoTimeoutError,
)
from domo_sdk.transport.auth import AuthStrategy

logger = logging.getLogger("domo_sdk.transport.sync")

DEFAULT_TIMEOUT = 60.0
SLOW_REQUEST_THRESHOLD = 5.0
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB


class SyncTransport:
    """Synchronous HTTP transport wrapping requests.Session.

    Delegates authentication to an AuthStrategy instance.
    Preserves CSV/gzip helpers from upstream pydomo.
    """

    def __init__(
        self,
        auth: AuthStrategy,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._auth = auth
        self._timeout = timeout
        self._session = requests.Session()

    def get_base_url(self) -> str:
        return self._auth.get_base_url()

    @property
    def auth_mode(self) -> str:
        return self._auth.auth_mode

    def _build_url(self, path: str) -> str:
        return self._auth.get_base_url() + path

    def _get_headers(self, content_type: str | None = None, accept: str = "application/json") -> dict[str, str]:
        headers = self._auth.get_headers()
        headers["Accept"] = accept
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _handle_response(self, response: requests.Response, url: str) -> Any:
        status = response.status_code

        if status == 401 or status == 403:
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

        return response

    def get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        headers = self._get_headers()
        full_url = self._build_url(url)
        start = time.time()
        try:
            response = self._session.get(full_url, headers=headers, params=params or {}, timeout=self._timeout)
            self._log_timing("GET", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def post(self, url: str, body: Any = None, params: dict[str, Any] | None = None) -> Any:
        headers = self._get_headers(content_type="application/json")
        full_url = self._build_url(url)
        data = json.dumps(body, default=str) if body is not None else None
        start = time.time()
        try:
            response = self._session.post(
                full_url, headers=headers, params=params or {}, data=data, timeout=self._timeout,
            )
            self._log_timing("POST", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def put(self, url: str, body: Any = None, params: dict[str, Any] | None = None) -> Any:
        headers = self._get_headers(content_type="application/json")
        full_url = self._build_url(url)
        data = json.dumps(body, default=str) if body is not None else None
        start = time.time()
        try:
            response = self._session.put(
                full_url, headers=headers, params=params or {}, data=data, timeout=self._timeout,
            )
            self._log_timing("PUT", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def patch(self, url: str, body: Any = None) -> Any:
        headers = self._get_headers(content_type="application/json")
        full_url = self._build_url(url)
        data = json.dumps(body, default=str) if body is not None else None
        start = time.time()
        try:
            response = self._session.patch(full_url, headers=headers, data=data, timeout=self._timeout)
            self._log_timing("PATCH", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def delete(self, url: str, params: dict[str, Any] | None = None) -> Any:
        headers = self._get_headers()
        full_url = self._build_url(url)
        start = time.time()
        try:
            response = self._session.delete(full_url, headers=headers, params=params or {}, timeout=self._timeout)
            self._log_timing("DELETE", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def put_csv(self, url: str, body: bytes | str) -> Any:
        headers = self._get_headers(content_type="text/csv")
        full_url = self._build_url(url)
        start = time.time()
        try:
            response = self._session.put(full_url, headers=headers, data=body, timeout=self._timeout)
            self._log_timing("PUT(csv)", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def put_gzip(self, url: str, body: bytes) -> Any:
        headers = self._get_headers(content_type="text/csv")
        headers["Content-Encoding"] = "gzip"
        full_url = self._build_url(url)
        start = time.time()
        try:
            response = self._session.put(full_url, headers=headers, data=body, timeout=self._timeout)
            self._log_timing("PUT(gzip)", url, time.time() - start)
            self._handle_response(response, url)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def get_csv(self, url: str, params: dict[str, Any] | None = None) -> str:
        headers = self._get_headers(accept="text/csv")
        full_url = self._build_url(url)
        start = time.time()
        try:
            response = self._session.get(full_url, headers=headers, params=params or {}, timeout=self._timeout)
            self._log_timing("GET(csv)", url, time.time() - start)
            self._handle_response(response, url)
            return response.text
        except requests.Timeout as err:
            raise DomoTimeoutError(url=url, timeout=self._timeout) from err
        except requests.ConnectionError as err:
            raise DomoConnectionError(url=url) from err

    def dump_response(self, response: requests.Response) -> str:
        data = dump.dump_all(response)
        return data.decode("utf-8")

    def _log_timing(self, method: str, url: str, duration: float) -> None:
        if duration > SLOW_REQUEST_THRESHOLD:
            logger.warning(f"Slow request: {method} {url} took {duration:.2f}s")
        else:
            logger.debug(f"{method} {url} completed in {duration:.2f}s")
