"""Async Projects and Tasks client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.projects import Project, Task, TaskList

URL_BASE = "/v1/projects"


class AsyncProjectsClient(AsyncDomoAPIClient):
    """Manage Domo projects, lists, and tasks asynchronously.

    Docs: https://developer.domo.com/docs/projects-api-reference/projects
    """

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    async def create_project(
        self, project_request: dict
    ) -> Project:
        """Create a new project."""
        data = await self._create(URL_BASE, project_request)
        return Project.model_validate(data)

    async def get_project(self, project_id: int) -> Project:
        """Retrieve a single project by ID."""
        data = await self._get(f"{URL_BASE}/{project_id}")
        return Project.model_validate(data)

    async def list_projects(
        self, per_page: int = 50, offset: int = 0
    ) -> list[Project]:
        """List all projects."""
        params: dict[str, Any] = {
            "limit": per_page,
            "offset": offset,
        }
        data = await self._list(URL_BASE, params=params)
        return [Project.model_validate(p) for p in data]

    async def update_project(
        self, project_id: int, project_update: dict
    ) -> Project:
        """Update an existing project."""
        data = await self._update(
            f"{URL_BASE}/{project_id}", project_update
        )
        return Project.model_validate(data)

    async def delete_project(self, project_id: int) -> None:
        """Delete a project."""
        await self._delete(f"{URL_BASE}/{project_id}")

    # ------------------------------------------------------------------
    # Lists
    # ------------------------------------------------------------------

    async def create_list(
        self, project_id: int, list_request: dict
    ) -> TaskList:
        """Create a new list within a project."""
        url = f"{URL_BASE}/{project_id}/lists"
        data = await self._create(url, list_request)
        return TaskList.model_validate(data)

    async def get_list(
        self, project_id: int, list_id: int
    ) -> TaskList:
        """Retrieve a specific list from a project."""
        url = f"{URL_BASE}/{project_id}/lists/{list_id}"
        data = await self._get(url)
        return TaskList.model_validate(data)

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    async def create_task(
        self, project_id: int, list_id: int, task_request: dict
    ) -> Task:
        """Create a new task within a project list."""
        url = f"{URL_BASE}/{project_id}/lists/{list_id}/tasks"
        data = await self._create(url, task_request)
        return Task.model_validate(data)

    async def get_task(
        self, project_id: int, list_id: int, task_id: int
    ) -> Task:
        """Retrieve a specific task."""
        url = (
            f"{URL_BASE}/{project_id}/lists/{list_id}/tasks/{task_id}"
        )
        data = await self._get(url)
        return Task.model_validate(data)

    async def update_task(
        self,
        project_id: int,
        list_id: int,
        task_id: int,
        task_update: dict,
    ) -> Task:
        """Update an existing task."""
        url = (
            f"{URL_BASE}/{project_id}/lists/{list_id}/tasks/{task_id}"
        )
        data = await self._update(url, task_update)
        return Task.model_validate(data)
