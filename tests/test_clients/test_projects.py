"""Tests for ProjectsClient with mocked transport."""
from __future__ import annotations

from unittest.mock import MagicMock

from domo_sdk.clients.projects import ProjectsClient
from domo_sdk.models.projects import Project, Task, TaskList


def _make_client() -> tuple[ProjectsClient, MagicMock]:
    transport = MagicMock()
    transport.auth_mode = "developer_token"
    return ProjectsClient(transport), transport


class TestProjectsCRUD:
    def test_create_project(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 1,
            "name": "Alpha",
        }

        result = client.create_project({"name": "Alpha"})

        assert isinstance(result, Project)
        assert result.name == "Alpha"

    def test_get_project(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {"id": 1, "name": "Alpha"}

        result = client.get_project(1)

        assert isinstance(result, Project)
        assert result.id == 1

    def test_list_projects(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
        ]

        result = client.list_projects()

        assert len(result) == 2
        assert all(isinstance(p, Project) for p in result)

    def test_update_project(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {
            "id": 1,
            "name": "Updated",
        }

        result = client.update_project(1, {"name": "Updated"})

        assert isinstance(result, Project)
        assert result.name == "Updated"

    def test_delete_project(self) -> None:
        client, transport = _make_client()
        client.delete_project(1)
        transport.delete.assert_called_once_with(
            "/v1/projects/1", params=None
        )


class TestProjectsLists:
    def test_create_list(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 10,
            "name": "Backlog",
        }

        result = client.create_list(1, {"name": "Backlog"})

        assert isinstance(result, TaskList)
        assert result.name == "Backlog"

    def test_get_list(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 10,
            "name": "Sprint 1",
        }

        result = client.get_list(1, 10)

        assert isinstance(result, TaskList)


class TestProjectsTasks:
    def test_create_task(self) -> None:
        client, transport = _make_client()
        transport.post.return_value = {
            "id": 100,
            "taskName": "Fix bug",
        }

        result = client.create_task(
            1, 10, {"taskName": "Fix bug"}
        )

        assert isinstance(result, Task)
        assert result.task_name == "Fix bug"

    def test_get_task(self) -> None:
        client, transport = _make_client()
        transport.get.return_value = {
            "id": 100,
            "taskName": "Fix bug",
        }

        result = client.get_task(1, 10, 100)

        assert isinstance(result, Task)

    def test_update_task(self) -> None:
        client, transport = _make_client()
        transport.put.return_value = {
            "id": 100,
            "taskName": "Updated",
        }

        result = client.update_task(
            1, 10, 100, {"taskName": "Updated"}
        )

        assert isinstance(result, Task)
        assert result.task_name == "Updated"
