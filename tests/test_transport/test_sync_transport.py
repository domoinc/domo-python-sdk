"""Tests for SyncTransport put/delete params support."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests

from domo_sdk.transport.auth import AuthStrategy
from domo_sdk.transport.sync_transport import SyncTransport


def _make_transport() -> tuple[SyncTransport, MagicMock]:
    """Create a SyncTransport with a mocked auth strategy and session."""
    auth = MagicMock(spec=AuthStrategy)
    auth.get_base_url.return_value = "https://api.domo.com"
    auth.get_headers.return_value = {"Authorization": "Bearer test"}
    auth.auth_mode = "developer_token"
    transport = SyncTransport(auth)
    return transport, auth


def _mock_response(status_code: int = 200, json_data: dict | list | None = None, content: bytes = b"{}") -> MagicMock:
    """Create a mock requests.Response."""
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.content = content
    response.text = content.decode() if content else ""
    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.return_value = {}
    return response


class TestPutWithParams:
    """Tests for put() with params support."""

    def test_put_passes_params(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"ok": True})

        with patch.object(transport._session, "put", return_value=mock_resp) as mock_put:
            result = transport.put("/test", body={"key": "val"}, params={"p": "1"})

        _, kwargs = mock_put.call_args
        assert kwargs["params"] == {"p": "1"}
        assert result == {"ok": True}

    def test_put_without_params_defaults_to_empty(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"ok": True})

        with patch.object(transport._session, "put", return_value=mock_resp) as mock_put:
            transport.put("/test", body=None)

        _, kwargs = mock_put.call_args
        assert kwargs["params"] == {}

    def test_put_with_none_params_defaults_to_empty(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"ok": True})

        with patch.object(transport._session, "put", return_value=mock_resp) as mock_put:
            transport.put("/test", body=None, params=None)

        _, kwargs = mock_put.call_args
        assert kwargs["params"] == {}


class TestDeleteWithParams:
    """Tests for delete() with params and return value support."""

    def test_delete_passes_params(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"Deleted": 3}, content=b'{"Deleted": 3}')

        with patch.object(transport._session, "delete", return_value=mock_resp) as mock_delete:
            result = transport.delete("/test", params={"ids": "1,2,3"})

        _, kwargs = mock_delete.call_args
        assert kwargs["params"] == {"ids": "1,2,3"}
        assert result == {"Deleted": 3}

    def test_delete_without_params_defaults_to_empty(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(204, content=b"")

        with patch.object(transport._session, "delete", return_value=mock_resp) as mock_delete:
            result = transport.delete("/test")

        _, kwargs = mock_delete.call_args
        assert kwargs["params"] == {}
        assert result is None

    def test_delete_returns_json_body(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, {"Created": 0, "Updated": 0, "Deleted": 5}, content=b'{"Created": 0}')

        with patch.object(transport._session, "delete", return_value=mock_resp):
            result = transport.delete("/test")

        assert result == {"Created": 0, "Updated": 0, "Deleted": 5}

    def test_delete_returns_none_on_204(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(204, content=b"")

        with patch.object(transport._session, "delete", return_value=mock_resp):
            result = transport.delete("/test")

        assert result is None

    def test_delete_returns_none_on_empty_content(self) -> None:
        transport, _ = _make_transport()
        mock_resp = _mock_response(200, content=b"")

        with patch.object(transport._session, "delete", return_value=mock_resp):
            result = transport.delete("/test")

        assert result is None
