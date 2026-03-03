"""Projects and tasks models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class Attachment(DomoModel):
    """Task attachment."""

    id: int | None = None
    name: str = ""
    size: int = 0
    created_by: int = Field(default=0, alias="createdBy")
    created_at: datetime | None = Field(default=None, alias="createdDate")


class Task(DomoModel):
    """Project task."""

    id: int | None = None
    task_name: str = Field(default="", alias="taskName")
    description: str = ""
    due_date: datetime | None = Field(default=None, alias="dueDate")
    priority: int = 0
    created_by: int = Field(default=0, alias="createdBy")
    created_at: datetime | None = Field(default=None, alias="createdDate")
    owned_by: int = Field(default=0, alias="ownedBy")
    tags: list[str] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)
    contributors: list[int] = Field(default_factory=list)


class TaskList(DomoModel):
    """A list of tasks within a project."""

    id: int | None = None
    name: str = ""
    index: int = 0
    tasks: list[Task] = Field(default_factory=list)


class Project(DomoModel):
    """Project response from API."""

    id: int | None = None
    name: str = ""
    description: str = ""
    created_at: datetime | None = Field(default=None, alias="createdDate")
    due_date: datetime | None = Field(default=None, alias="dueDate")
    members: list[dict[str, Any]] = Field(default_factory=list)
    public: bool = False
    task_lists: list[TaskList] = Field(default_factory=list, alias="lists")
