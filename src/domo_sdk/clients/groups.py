"""Group client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.groups import Group

URL_BASE = "/v1/groups"


class GroupClient(DomoAPIClient):
    """Manage Domo groups.

    Docs: https://developer.domo.com/docs/groups-api-reference/groups-2
    """

    def create(self, group_request: dict) -> Group:
        """Create a new group."""
        data = self._create(URL_BASE, group_request)
        return Group.model_validate(data)

    def get(self, group_id: int) -> Group:
        """Retrieve a single group by ID."""
        data = self._get(f"{URL_BASE}/{group_id}")
        return Group.model_validate(data)

    def list(
        self, per_page: int = 50, offset: int = 0
    ) -> list[Group]:
        """List groups."""
        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        data = self._list(URL_BASE, params=params)
        return [Group.model_validate(g) for g in data]

    def update(self, group_id: int, group_update: dict) -> Group:
        """Update an existing group."""
        data = self._update(f"{URL_BASE}/{group_id}", group_update)
        return Group.model_validate(data)

    def delete(self, group_id: int) -> None:
        """Delete a group."""
        self._delete(f"{URL_BASE}/{group_id}")

    def add_user(self, group_id: int, user_id: int) -> None:
        """Add a user to a group."""
        self._update(f"{URL_BASE}/{group_id}/users/{user_id}", None)

    def remove_user(self, group_id: int, user_id: int) -> None:
        """Remove a user from a group."""
        self._delete(f"{URL_BASE}/{group_id}/users/{user_id}")

    def list_users(
        self, group_id: int, limit: int = 50, offset: int = 0
    ) -> list[int]:
        """List user IDs in a group."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        return self._list(f"{URL_BASE}/{group_id}/users", params=params)
