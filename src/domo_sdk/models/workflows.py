"""Workflow models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class WorkflowPermission(DomoModel):
    """Workflow permission entry."""

    type: str = ""  # "USER" or "GROUP"
    id: int = 0
    permissions: list[str] = Field(default_factory=list)


class WorkflowModel(DomoModel):
    """Workflow model definition."""

    id: int | None = None
    name: str = ""
    description: str = ""
    version: int = 0
    owner: dict[str, Any] | None = None


class WorkflowInstance(DomoModel):
    """Running workflow instance."""

    id: str = ""
    model_id: int = Field(default=0, alias="modelId")
    status: str = ""  # "RUNNING", "COMPLETED", "CANCELLED", "FAILED"
    started_at: datetime | None = Field(default=None, alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    started_by: int = Field(default=0, alias="startedBy")
    parameters: dict[str, Any] = Field(default_factory=dict)
