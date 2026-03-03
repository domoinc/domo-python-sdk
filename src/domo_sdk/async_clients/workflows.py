"""Async Workflows client for the Domo API."""

from __future__ import annotations

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.workflows import WorkflowInstance, WorkflowPermission

URL_BASE = "/v1/workflows"


class AsyncWorkflowsClient(AsyncDomoAPIClient):
    """Manage Domo workflows asynchronously.

    Docs: https://developer.domo.com/docs/workflows-api-reference/workflows
    """

    async def start(
        self, workflow_id: int, body: dict | None = None
    ) -> WorkflowInstance:
        """Start a workflow execution."""
        url = f"{URL_BASE}/{workflow_id}/start"
        data = await self._create(url, body or {})
        return WorkflowInstance.model_validate(data)

    async def get_instance(
        self, workflow_id: int, instance_id: int
    ) -> WorkflowInstance:
        """Get a specific workflow instance."""
        url = f"{URL_BASE}/{workflow_id}/instances/{instance_id}"
        data = await self._get(url)
        return WorkflowInstance.model_validate(data)

    async def cancel(
        self, workflow_id: int, instance_id: int
    ) -> None:
        """Cancel a running workflow instance."""
        url = (
            f"{URL_BASE}/{workflow_id}/instances/{instance_id}/cancel"
        )
        await self._create(url, {})

    async def get_permissions(
        self, workflow_id: int
    ) -> list[WorkflowPermission]:
        """Get permissions for a workflow."""
        url = f"{URL_BASE}/{workflow_id}/permissions"
        data = await self._get(url)
        return [WorkflowPermission.model_validate(p) for p in data]

    async def set_permissions(
        self, workflow_id: int, permissions: list
    ) -> None:
        """Set permissions for a workflow."""
        url = f"{URL_BASE}/{workflow_id}/permissions"
        await self._update(url, permissions)
