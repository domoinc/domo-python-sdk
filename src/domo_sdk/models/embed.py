"""Embed token models."""

from __future__ import annotations

from pydantic import Field

from domo_sdk.models.base import DomoModel


class EmbedPermission(DomoModel):
    """Embed permission."""

    permission: str = ""  # "READ", "FILTER", "EXPORT"


class EmbedPolicy(DomoModel):
    """Embed policy with filters."""

    column: str = ""
    operator: str = ""
    values: list[str] = Field(default_factory=list)


class EmbedToken(DomoModel):
    """Embed authentication token."""

    token: str = ""
    expiration: int = 0
    policies: list[EmbedPolicy] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
