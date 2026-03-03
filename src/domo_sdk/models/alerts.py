"""Alert models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class AlertRule(DomoModel):
    """Alert trigger rule."""

    condition: str = ""
    value: float | str | None = None
    operator: str = ""


class AlertSubscription(DomoModel):
    """Alert subscription entry."""

    user_id: int = Field(alias="userId")
    subscribed: bool = True


class Alert(DomoModel):
    """Alert response from API."""

    id: int
    name: str = ""
    description: str = ""
    type: str = ""
    dataset_id: str = Field(default="", alias="dataSetId")
    card_id: int | None = Field(default=None, alias="cardId")
    owner: dict[str, Any] | None = None
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    triggered: bool = False
    rules: list[AlertRule] = Field(default_factory=list)
    subscribers: list[AlertSubscription] = Field(default_factory=list)
