"""Roles client for the Domo API."""

from __future__ import annotations

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.roles import Authority, Role

URL_BASE = "/authorization/v1/roles"


class RolesClient(DomoAPIClient):
    """Manage Domo roles and authorities.

    Docs: https://developer.domo.com/docs/roles-api-reference/roles
    """

    def list(self) -> list[Role]:
        """List all roles."""
        data = self._list(URL_BASE)
        return [Role.model_validate(r) for r in data]

    def create(self, role_data: dict) -> Role:
        """Create a new role."""
        data = self._create(URL_BASE, role_data)
        return Role.model_validate(data)

    def get(self, role_id: int) -> Role:
        """Retrieve a single role by ID."""
        data = self._get(f"{URL_BASE}/{role_id}")
        return Role.model_validate(data)

    def delete(self, role_id: int) -> None:
        """Delete a role."""
        self._delete(f"{URL_BASE}/{role_id}")

    def list_authorities(self, role_id: int) -> list[Authority]:
        """List authorities granted to a role."""
        data = self._get(f"{URL_BASE}/{role_id}/authorities")
        return [Authority.model_validate(a) for a in data]

    def update_authorities(
        self, role_id: int, authorities: list[dict]
    ) -> list[Authority]:
        """Update (patch) the authorities for a role."""
        url = f"{URL_BASE}/{role_id}/authorities"
        data = self._update(url, authorities, method="PATCH")
        return [Authority.model_validate(a) for a in data]
