"""Card models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class CardType(DomoModel):
    """Card chart type."""

    type: str = ""
    sub_type: str = Field(default="", alias="subType")


class DrillPathField(DomoModel):
    """Field in a drill path."""

    dataset_id: str = Field(alias="dataSetId")
    column: str


class DrillPath(DomoModel):
    """Card drill path definition."""

    id: int | None = None
    name: str = ""
    fields: list[DrillPathField] = Field(default_factory=list)


class Card(DomoModel):
    """Card response from API."""

    id: int
    name: str = Field(default="", alias="title")
    description: str = ""
    type: str = ""
    owners: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    dataset_id: str = Field(default="", alias="dataSetId")
    drill_paths: list[DrillPath] = Field(
        default_factory=list, alias="drillPaths"
    )
