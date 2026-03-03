"""Tests for AsyncS3ExportClient using respx."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from domo_sdk.async_clients.s3_export import AsyncS3ExportClient
from domo_sdk.models.s3_export import S3Export
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
)


def _make_async_client() -> tuple[AsyncS3ExportClient, str]:
    creds = DeveloperTokenCredentials(
        token="test-token", instance_domain="test.domo.com"
    )
    strategy = DeveloperTokenStrategy(credentials=creds)
    transport = AsyncTransport(auth=strategy)
    client = AsyncS3ExportClient(transport)
    base_url = strategy.get_base_url()
    return client, base_url


@pytest.mark.asyncio
class TestAsyncS3Export:
    @respx.mock
    async def test_start_export(self) -> None:
        client, base_url = _make_async_client()
        route = respx.post(
            f"{base_url}/v1/datasets/ds-1/exports"
        ).mock(
            return_value=Response(
                200,
                json={
                    "exportId": "exp-1",
                    "datasetId": "ds-1",
                    "status": "STARTED",
                },
            )
        )

        result = await client.start_export(
            "ds-1", {"bucket": "my-bucket"}
        )

        assert route.called
        assert isinstance(result, S3Export)
        assert result.status == "STARTED"
        await client.transport.close()

    @respx.mock
    async def test_get_export_status(self) -> None:
        client, base_url = _make_async_client()
        route = respx.get(
            f"{base_url}/v1/datasets/ds-1/exports/exp-1"
        ).mock(
            return_value=Response(
                200,
                json={
                    "exportId": "exp-1",
                    "datasetId": "ds-1",
                    "status": "COMPLETED",
                },
            )
        )

        result = await client.get_export_status("ds-1", "exp-1")

        assert route.called
        assert isinstance(result, S3Export)
        assert result.status == "COMPLETED"
        await client.transport.close()
