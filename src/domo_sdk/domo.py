"""Main entry points: Domo (sync) and AsyncDomo (async)."""

from __future__ import annotations

import logging
import os
from typing import Any

from domo_sdk.async_clients.accounts import AsyncAccountClient
from domo_sdk.async_clients.activity_log import AsyncActivityLogClient
from domo_sdk.async_clients.ai import AsyncAIClient
from domo_sdk.async_clients.alerts import AsyncAlertsClient
from domo_sdk.async_clients.appdb import AsyncAppDBClient
from domo_sdk.async_clients.cards import AsyncCardClient
from domo_sdk.async_clients.connectors import AsyncConnectorsClient
from domo_sdk.async_clients.dataflows import AsyncDataflowsClient

# Async clients
from domo_sdk.async_clients.datasets import AsyncDataSetClient
from domo_sdk.async_clients.embed import AsyncEmbedClient
from domo_sdk.async_clients.files import AsyncFilesClient
from domo_sdk.async_clients.groups import AsyncGroupClient
from domo_sdk.async_clients.pages import AsyncPageClient
from domo_sdk.async_clients.projects import AsyncProjectsClient
from domo_sdk.async_clients.roles import AsyncRolesClient
from domo_sdk.async_clients.s3_export import AsyncS3ExportClient
from domo_sdk.async_clients.search import AsyncSearchClient
from domo_sdk.async_clients.streams import AsyncStreamClient
from domo_sdk.async_clients.users import AsyncUserClient
from domo_sdk.async_clients.workflows import AsyncWorkflowsClient
from domo_sdk.clients.accounts import AccountClient
from domo_sdk.clients.activity_log import ActivityLogClient
from domo_sdk.clients.ai import AIClient
from domo_sdk.clients.alerts import AlertsClient
from domo_sdk.clients.appdb import AppDBClient
from domo_sdk.clients.cards import CardClient
from domo_sdk.clients.connectors import ConnectorsClient
from domo_sdk.clients.dataflows import DataflowsClient

# Sync clients
from domo_sdk.clients.datasets import DataSetClient
from domo_sdk.clients.embed import EmbedClient
from domo_sdk.clients.files import FilesClient
from domo_sdk.clients.groups import GroupClient
from domo_sdk.clients.pages import PageClient
from domo_sdk.clients.projects import ProjectsClient
from domo_sdk.clients.roles import RolesClient
from domo_sdk.clients.s3_export import S3ExportClient
from domo_sdk.clients.search import SearchClient
from domo_sdk.clients.streams import StreamClient
from domo_sdk.clients.users import UserClient
from domo_sdk.clients.workflows import WorkflowsClient
from domo_sdk.exceptions import DomoValidationError
from domo_sdk.transport.async_transport import AsyncTransport
from domo_sdk.transport.auth import (
    DeveloperTokenCredentials,
    DeveloperTokenStrategy,
    OAuthCredentials,
    OAuthStrategy,
)
from domo_sdk.transport.sync_transport import SyncTransport

logger = logging.getLogger("domo_sdk")


def _build_auth_strategy(
    client_id: str | None = None,
    client_secret: str | None = None,
    developer_token: str | None = None,
    instance_domain: str | None = None,
    api_host: str = "api.domo.com",
    use_https: bool = True,
    request_timeout: float | None = None,
    scope: list[str] | None = None,
) -> DeveloperTokenStrategy | OAuthStrategy:
    """Build auth strategy from provided credentials."""
    if developer_token and instance_domain:
        return DeveloperTokenStrategy(
            DeveloperTokenCredentials(token=developer_token, instance_domain=instance_domain)
        )
    elif client_id and client_secret:
        return OAuthStrategy(
            OAuthCredentials(client_id=client_id, client_secret=client_secret, scope=scope),
            api_host=api_host,
            use_https=use_https,
            request_timeout=request_timeout,
        )
    else:
        raise DomoValidationError(
            message="Missing credentials. Provide either "
            "(developer_token + instance_domain) or (client_id + client_secret)."
        )


def _auth_from_env(
    request_timeout: float | None = None,
    scope: list[str] | None = None,
) -> DeveloperTokenStrategy | OAuthStrategy:
    """Build auth strategy from environment variables."""
    developer_token = os.getenv("DOMO_DEVELOPER_TOKEN")
    instance_domain = os.getenv("DOMO_HOST", "")

    client_id = os.getenv("DOMO_CLIENT_ID")
    client_secret = os.getenv("DOMO_CLIENT_SECRET")

    return _build_auth_strategy(
        client_id=client_id,
        client_secret=client_secret,
        developer_token=developer_token,
        instance_domain=instance_domain,
        request_timeout=request_timeout,
        scope=scope,
    )


class Domo:
    """Synchronous Domo SDK client.

    Provides access to all Domo API endpoints through sub-clients.

    Usage:
        domo = Domo(client_id="...", client_secret="...")
        datasets = list(domo.datasets.list())

        domo = Domo(developer_token="...", instance_domain="instance.domo.com")
        roles = domo.roles.list()

        domo = Domo.from_env()
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        developer_token: str | None = None,
        instance_domain: str | None = None,
        api_host: str = "api.domo.com",
        use_https: bool = True,
        request_timeout: float | None = None,
        scope: list[str] | None = None,
        log_level: int | None = None,
    ) -> None:
        if log_level:
            logger.setLevel(log_level)

        auth = _build_auth_strategy(
            client_id=client_id,
            client_secret=client_secret,
            developer_token=developer_token,
            instance_domain=instance_domain,
            api_host=api_host,
            use_https=use_https,
            request_timeout=request_timeout,
            scope=scope,
        )

        self.transport = SyncTransport(auth=auth, timeout=request_timeout or 60.0)
        self._init_clients()

    def _init_clients(self) -> None:
        self.datasets = DataSetClient(self.transport)
        self.users = UserClient(self.transport)
        self.groups = GroupClient(self.transport)
        self.pages = PageClient(self.transport)
        self.streams = StreamClient(self.transport)
        self.accounts = AccountClient(self.transport)
        self.roles = RolesClient(self.transport)
        self.search = SearchClient(self.transport)
        self.cards = CardClient(self.transport)
        self.activity_log = ActivityLogClient(self.transport)
        self.projects = ProjectsClient(self.transport)
        self.alerts = AlertsClient(self.transport)
        self.workflows = WorkflowsClient(self.transport)
        self.dataflows = DataflowsClient(self.transport)
        self.connectors = ConnectorsClient(self.transport)
        self.embed = EmbedClient(self.transport)
        self.files = FilesClient(self.transport)
        self.s3_export = S3ExportClient(self.transport)
        self.ai = AIClient(self.transport)
        self.appdb = AppDBClient(self.transport)

    @classmethod
    def from_env(
        cls,
        request_timeout: float | None = None,
        scope: list[str] | None = None,
        log_level: int | None = None,
    ) -> Domo:
        """Create Domo client from environment variables.

        Looks for:
        - DOMO_DEVELOPER_TOKEN + DOMO_HOST (developer token auth)
        - DOMO_CLIENT_ID + DOMO_CLIENT_SECRET (OAuth auth)
        """
        developer_token = os.getenv("DOMO_DEVELOPER_TOKEN")
        instance_domain = os.getenv("DOMO_HOST", "")
        client_id = os.getenv("DOMO_CLIENT_ID")
        client_secret = os.getenv("DOMO_CLIENT_SECRET")

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            developer_token=developer_token,
            instance_domain=instance_domain,
            request_timeout=request_timeout,
            scope=scope,
            log_level=log_level,
        )


class AsyncDomo:
    """Asynchronous Domo SDK client.

    Provides access to all Domo API endpoints through async sub-clients.
    Implements async context manager for resource cleanup.

    Usage:
        async with AsyncDomo(developer_token="...", instance_domain="...") as domo:
            datasets = await domo.datasets.list()

        async with AsyncDomo.from_env() as domo:
            result = await domo.ai.text.generate({"prompt": "..."})
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        developer_token: str | None = None,
        instance_domain: str | None = None,
        api_host: str = "api.domo.com",
        use_https: bool = True,
        request_timeout: float | None = None,
        scope: list[str] | None = None,
        log_level: int | None = None,
    ) -> None:
        if log_level:
            logger.setLevel(log_level)

        auth = _build_auth_strategy(
            client_id=client_id,
            client_secret=client_secret,
            developer_token=developer_token,
            instance_domain=instance_domain,
            api_host=api_host,
            use_https=use_https,
            request_timeout=request_timeout,
            scope=scope,
        )

        self.transport = AsyncTransport(
            auth=auth,
            timeout=request_timeout or 60.0,
        )
        self._init_clients()

    def _init_clients(self) -> None:
        self.datasets = AsyncDataSetClient(self.transport)
        self.users = AsyncUserClient(self.transport)
        self.groups = AsyncGroupClient(self.transport)
        self.pages = AsyncPageClient(self.transport)
        self.streams = AsyncStreamClient(self.transport)
        self.accounts = AsyncAccountClient(self.transport)
        self.roles = AsyncRolesClient(self.transport)
        self.search = AsyncSearchClient(self.transport)
        self.cards = AsyncCardClient(self.transport)
        self.activity_log = AsyncActivityLogClient(self.transport)
        self.projects = AsyncProjectsClient(self.transport)
        self.alerts = AsyncAlertsClient(self.transport)
        self.workflows = AsyncWorkflowsClient(self.transport)
        self.dataflows = AsyncDataflowsClient(self.transport)
        self.connectors = AsyncConnectorsClient(self.transport)
        self.embed = AsyncEmbedClient(self.transport)
        self.files = AsyncFilesClient(self.transport)
        self.s3_export = AsyncS3ExportClient(self.transport)
        self.ai = AsyncAIClient(self.transport)
        self.appdb = AsyncAppDBClient(self.transport)

    async def close(self) -> None:
        """Close the underlying transport."""
        await self.transport.close()

    async def __aenter__(self) -> AsyncDomo:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    @classmethod
    def from_env(
        cls,
        request_timeout: float | None = None,
        scope: list[str] | None = None,
        log_level: int | None = None,
    ) -> AsyncDomo:
        """Create AsyncDomo client from environment variables.

        Looks for:
        - DOMO_DEVELOPER_TOKEN + DOMO_HOST (developer token auth)
        - DOMO_CLIENT_ID + DOMO_CLIENT_SECRET (OAuth auth)
        """
        developer_token = os.getenv("DOMO_DEVELOPER_TOKEN")
        instance_domain = os.getenv("DOMO_HOST", "")
        client_id = os.getenv("DOMO_CLIENT_ID")
        client_secret = os.getenv("DOMO_CLIENT_SECRET")

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            developer_token=developer_token,
            instance_domain=instance_domain,
            request_timeout=request_timeout,
            scope=scope,
            log_level=log_level,
        )
