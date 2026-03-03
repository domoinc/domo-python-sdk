"""Tests for AsyncTransport put/delete params support."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import AuthStrategy


def _make_transport() -> tuple[AsyncTransport, MagicMock]:
    """Create an AsyncTransport with a mocked auth strategy."""
    auth = MagicMock(spec=AuthStrategy)
    auth.get_base_url.return_value = "https://api.domo.com"
    auth.get_headers_async = AsyncMock(return_value={"Authorization": "Bearer test"})
    auth.auth_mode = "developer_token"
    transport = AsyncTransport(auth)
    return transport, auth


def _mock_response(status_code: int = 200, json_data: dict | list | None = None, content: bytes = b"{}") -> MagicMock:
    """Create a mock httpx.Response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.content = content
    response.text = content.decode() if content else ""
    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.return_value = {}
    return response


class TestPutWithParams:
    """Tests for async put() with params support."""

    @pytest.mark.asyncio
    async def test_put_passes_params(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"ok": True})
        mock_client = AsyncMock()
        mock_client.put.return_value = mock_resp
        mock_client.is_closed = False

        with patch.object(transport, "_get_client", return_value=mock_client):
            result = await transport.put("/test", body={"key": "val"}, params={"p": "1"})

        _, kwargs = mock_client.put.call_args
        assert kwargs["params"] == {"p": "1"}
        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_put_without_params_defaults_to_empty(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"ok": True})
        mock_client = AsyncMock()
        mock_client.put.return_value = mock_resp
        mock_client.is_closed = False

        with patch.object(transport, "_get_client", return_value=mock_client):
            await transport.put("/test", body=None)

        _, kwargs = mock_client.put.call_args
        assert kwargs["params"] == {}


class TestDeleteWithParams:
    """Tests for async delete() with params and return value support."""

    @pytest.mark.asyncio
    async def test_delete_passes_params(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"Deleted": 3}, content=b'{"Deleted": 3}')
        mock_client = AsyncMock()
        mock_client.delete.return_value = mock_resp
        mock_client.is_closed = False

        with patch.object(transport, "_get_client", return_value=mock_client):
            result = await transport.delete("/test", params={"ids": "1,2,3"})

        _, kwargs = mock_client.delete.call_args
        assert kwargs["params"] == {"ids": "1,2,3"}
        assert result == {"Deleted": 3}

    @pytest.mark.asyncio
    async def test_delete_returns_none_on_204(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(204, content=b"")
        mock_client = AsyncMock()
        mock_client.delete.return_value = mock_resp
        mock_client.is_closed = False

        with patch.object(transport, "_get_client", return_value=mock_client):
            result = await transport.delete("/test")

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_returns_json_body(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"Deleted": 5}, content=b'{"Deleted": 5}')
        mock_client = AsyncMock()
        mock_client.delete.return_value = mock_resp
        mock_client.is_closed = False

        with patch.object(transport, "_get_client", return_value=mock_client):
            result = await transport.delete("/test")

        assert result == {"Deleted": 5}

    @pytest.mark.asyncio
    async def test_delete_returns_none_on_empty_content(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, content=b"")
        mock_client = AsyncMock()
        mock_client.delete.return_value = mock_resp
        mock_client.is_closed = False

        with patch.object(transport, "_get_client", return_value=mock_client):
            result = await transport.delete("/test")

        assert result is None
