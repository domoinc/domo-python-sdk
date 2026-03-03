"""Files and filesets models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class FileRevision(DomoModel):
    """File revision."""

    id: int = 0
    revision_number: int = Field(default=0, alias="revisionNumber")
    size: int = 0
    created_at: datetime | None = Field(default=None, alias="createdAt")


class File(DomoModel):
    """File metadata."""

    id: int = 0
    name: str = ""
    description: str = ""
    content_type: str = Field(default="", alias="contentType")
    size: int = 0
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    revisions: list[FileRevision] = Field(default_factory=list)
    owner: dict[str, Any] | None = None


class FileSet(DomoModel):
    """File set container."""

    id: int = 0
    name: str = ""
    description: str = ""
    created_at: datetime | None = Field(default=None, alias="createdAt")
