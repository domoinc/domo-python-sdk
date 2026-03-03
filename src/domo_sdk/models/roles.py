"""Role and governance models."""

from __future__ import annotations

from pydantic import Field

from domo_sdk.models.base import DomoModel


class Authority(DomoModel):
    """Role authority."""

    authority: str
    grant_type: str = ""


class CreateRoleRequest(DomoModel):
    """Request to create a role."""

    name: str
    description: str = ""


class Role(DomoModel):
    """Role response from API."""

    id: int
    name: str = ""
    description: str = ""
    is_system: bool = False
    user_count: int = 0
    authorities: list[Authority] = Field(default_factory=list)
