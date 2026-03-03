"""Workflows client for the Domo API."""

from __future__ import annotations

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.workflows import WorkflowInstance, WorkflowPermission

URL_BASE = "/workflow/v1"


class WorkflowsClient(DomoAPIClient):
    """Manage Domo workflows.

    Docs: https://developer.domo.com/docs/workflows-api-reference/workflows
    """

    def start(self, message_data: dict) -> WorkflowInstance:
        """Start a workflow by sending a message."""
        data = self._create(
            f"{URL_BASE}/instances/message", message_data
        )
        return WorkflowInstance.model_validate(data)

    def get_instance(self, instance_id: str) -> WorkflowInstance:
        """Retrieve a workflow instance by ID."""
        data = self._get(f"{URL_BASE}/instances/{instance_id}")
        return WorkflowInstance.model_validate(data)

    def cancel(self, instance_id: str) -> None:
        """Cancel a running workflow instance."""
        self._create(
            f"{URL_BASE}/instances/{instance_id}/cancel", None
        )

    def get_permissions(
        self, model_id: int
    ) -> list[WorkflowPermission]:
        """Get permissions for a workflow model."""
        data = self._get(
            f"{URL_BASE}/models/{model_id}/permissions"
        )
        return [WorkflowPermission.model_validate(p) for p in data]

    def set_permissions(
        self, model_id: int, permissions: list
    ) -> None:
        """Set permissions for a workflow model."""
        self._create(
            f"{URL_BASE}/models/{model_id}/permissions", permissions
        )
