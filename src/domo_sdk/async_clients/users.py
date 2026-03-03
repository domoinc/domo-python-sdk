"""Async User client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.users import User

URL_BASE = "/v1/users"


class AsyncUserClient(AsyncDomoAPIClient):
    """Manage Domo users asynchronously.

    Docs: https://developer.domo.com/docs/users-api-reference/users-2
    """

    async def create(
        self, user_request: dict, send_invite: bool = False
    ) -> User:
        """Create a new user."""
        data = await self._create(
            URL_BASE, user_request, params={"sendInvite": send_invite}
        )
        return User.model_validate(data)

    async def get(self, user_id: int) -> User:
        """Retrieve a single user by ID."""
        data = await self._get(f"{URL_BASE}/{user_id}")
        return User.model_validate(data)

    async def list(
        self,
        per_page: int = 50,
        offset: int = 0,
        limit: int = 0,
    ) -> list[User]:
        """Return a full list of users, paginating internally."""
        if per_page not in range(1, 51):
            raise ValueError(
                "per_page must be between 1 and 50 (inclusive)"
            )

        if limit:
            per_page = min(per_page, limit)

        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        result: list[User] = []
        users: list[dict] = await self._list(URL_BASE, params=params)

        while users:
            for user in users:
                result.append(User.model_validate(user))
                if limit and len(result) >= limit:
                    return result

            params["offset"] += per_page
            if limit and params["offset"] + per_page > limit:
                params["limit"] = limit - params["offset"]
            users = await self._list(URL_BASE, params=params)

        return result

    async def update(self, user_id: int, user_update: dict) -> User:
        """Update an existing user."""
        data = await self._update(
            f"{URL_BASE}/{user_id}", user_update
        )
        return User.model_validate(data)

    async def delete(self, user_id: int) -> None:
        """Delete a user."""
        await self._delete(f"{URL_BASE}/{user_id}")
