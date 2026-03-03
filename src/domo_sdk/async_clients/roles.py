"""Async Roles client for the Domo API."""

from __future__ import annotations

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.roles import Authority, Role

URL_BASE = "/authorization/v1/roles"


class AsyncRolesClient(AsyncDomoAPIClient):
    """Manage Domo roles and authorities asynchronously.

    Docs: https://developer.domo.com/docs/roles-api-reference/roles
    """

    async def list(self) -> list[Role]:
        """List all roles."""
        data = await self._list(URL_BASE)
        return [Role.model_validate(r) for r in data]

    async def create(self, role_data: dict) -> Role:
        """Create a new role."""
        data = await self._create(URL_BASE, role_data)
        return Role.model_validate(data)

    async def get(self, role_id: int) -> Role:
        """Retrieve a single role by ID."""
        data = await self._get(f"{URL_BASE}/{role_id}")
        return Role.model_validate(data)

    async def delete(self, role_id: int) -> None:
        """Delete a role."""
        await self._delete(f"{URL_BASE}/{role_id}")

    async def list_authorities(self, role_id: int) -> list[Authority]:
        """List authorities granted to a role."""
        data = await self._get(f"{URL_BASE}/{role_id}/authorities")
        return [Authority.model_validate(a) for a in data]

    async def update_authorities(
        self, role_id: int, authorities: list[dict]
    ) -> list[Authority]:
        """Update (patch) the authorities for a role."""
        url = f"{URL_BASE}/{role_id}/authorities"
        data = await self._update(url, authorities, method="PATCH")
        return [Authority.model_validate(a) for a in data]
