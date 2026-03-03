"""Projects and tasks client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.projects import Project, Task, TaskList

URL_BASE = "/v1/projects"


class ProjectsClient(DomoAPIClient):
    """Manage Domo projects, lists, and tasks.

    Docs: https://developer.domo.com/docs/projects-api-reference/projects
    """

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def create_project(self, project_data: dict) -> Project:
        """Create a new project."""
        data = self._create(URL_BASE, project_data)
        return Project.model_validate(data)

    def get_project(self, project_id: int) -> Project:
        """Retrieve a single project by ID."""
        data = self._get(f"{URL_BASE}/{project_id}")
        return Project.model_validate(data)

    def list_projects(
        self, per_page: int = 50, offset: int = 0
    ) -> list[Project]:
        """List projects."""
        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        data = self._list(URL_BASE, params=params)
        return [Project.model_validate(p) for p in data]

    def update_project(
        self, project_id: int, project_update: dict
    ) -> Project:
        """Update an existing project."""
        data = self._update(
            f"{URL_BASE}/{project_id}", project_update
        )
        return Project.model_validate(data)

    def delete_project(self, project_id: int) -> None:
        """Delete a project."""
        self._delete(f"{URL_BASE}/{project_id}")

    # ------------------------------------------------------------------
    # Lists
    # ------------------------------------------------------------------

    def create_list(
        self, project_id: int, list_data: dict
    ) -> TaskList:
        """Create a list within a project."""
        data = self._create(
            f"{URL_BASE}/{project_id}/lists", list_data
        )
        return TaskList.model_validate(data)

    def get_list(self, project_id: int, list_id: int) -> TaskList:
        """Retrieve a single list by ID."""
        data = self._get(
            f"{URL_BASE}/{project_id}/lists/{list_id}"
        )
        return TaskList.model_validate(data)

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    def create_task(
        self, project_id: int, list_id: int, task_data: dict
    ) -> Task:
        """Create a task within a project list."""
        data = self._create(
            f"{URL_BASE}/{project_id}/lists/{list_id}/tasks",
            task_data,
        )
        return Task.model_validate(data)

    def get_task(
        self, project_id: int, list_id: int, task_id: int
    ) -> Task:
        """Retrieve a single task by ID."""
        data = self._get(
            f"{URL_BASE}/{project_id}/lists/{list_id}/tasks/{task_id}"
        )
        return Task.model_validate(data)

    def update_task(
        self,
        project_id: int,
        list_id: int,
        task_id: int,
        task_update: dict,
    ) -> Task:
        """Update an existing task."""
        data = self._update(
            f"{URL_BASE}/{project_id}/lists/{list_id}/tasks/{task_id}",
            task_update,
        )
        return Task.model_validate(data)
