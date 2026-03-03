"""Async Group client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.groups import Group

URL_BASE = "/v1/groups"


class AsyncGroupClient(AsyncDomoAPIClient):
    """Manage Domo groups asynchronously.

    Docs: https://developer.domo.com/docs/groups-api-reference/groups
    """

    async def create(self, group_request: dict) -> Group:
        """Create a new group."""
        data = await self._create(URL_BASE, group_request)
        return Group.model_validate(data)

    async def get(self, group_id: int) -> Group:
        """Retrieve a single group by ID."""
        data = await self._get(f"{URL_BASE}/{group_id}")
        return Group.model_validate(data)

    async def list(
        self, per_page: int = 50, offset: int = 0
    ) -> list[Group]:
        """Return a full list of groups, paginating internally."""
        if per_page not in range(1, 51):
            raise ValueError(
                "per_page must be between 1 and 50 (inclusive)"
            )

        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        result: list[Group] = []
        groups: list[dict] = await self._list(URL_BASE, params=params)

        while groups:
            for group in groups:
                result.append(Group.model_validate(group))

            params["offset"] += per_page
            groups = await self._list(URL_BASE, params=params)

        return result

    async def update(
        self, group_id: int, group_update: dict
    ) -> Group:
        """Update an existing group."""
        data = await self._update(
            f"{URL_BASE}/{group_id}", group_update
        )
        return Group.model_validate(data)

    async def delete(self, group_id: int) -> None:
        """Delete a group."""
        await self._delete(f"{URL_BASE}/{group_id}")

    async def add_user(self, group_id: int, user_id: int) -> None:
        """Add a user to a group."""
        url = f"{URL_BASE}/{group_id}/users/{user_id}"
        await self._update(url, None)

    async def remove_user(
        self, group_id: int, user_id: int
    ) -> None:
        """Remove a user from a group."""
        url = f"{URL_BASE}/{group_id}/users/{user_id}"
        await self._delete(url)

    async def list_users(
        self, group_id: int, limit: int = 50, offset: int = 0
    ) -> list[int]:
        """List user IDs in a group."""
        url = f"{URL_BASE}/{group_id}/users"
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        return await self._list(url, params=params)
