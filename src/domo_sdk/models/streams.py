"""Stream models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel
from domo_sdk.models.datasets import UpdateMethod


class StreamExecution(DomoModel):
    """Stream execution details."""

    id: int = 0
    start_time: datetime | None = Field(
        default=None, alias="startedAt"
    )
    end_time: datetime | None = Field(default=None, alias="endedAt")
    current_state: str = Field(default="", alias="currentState")
    rows: int = 0
    update_method: str = Field(default="", alias="updateMethod")


class Stream(DomoModel):
    """Stream response from API."""

    id: int = 0
    dataset: dict[str, Any] | None = Field(
        default=None, alias="dataSet"
    )
    update_method: UpdateMethod = Field(
        default=UpdateMethod.REPLACE, alias="updateMethod"
    )
    created_at: datetime | None = Field(
        default=None, alias="createdAt"
    )
    modified_at: datetime | None = Field(
        default=None, alias="modifiedAt"
    )
