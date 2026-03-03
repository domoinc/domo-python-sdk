"""Async Account client for the Domo API."""

from __future__ import annotations

from typing import Any

from domo_sdk.async_clients.base import AsyncDomoAPIClient
from domo_sdk.models.accounts import Account

URL_BASE = "/v1/accounts"


class AsyncAccountClient(AsyncDomoAPIClient):
    """Manage Domo accounts asynchronously.

    Docs: https://developer.domo.com/docs/accounts-api-reference/accounts
    """

    async def create(self, **kwargs: Any) -> Account:
        """Create a new account."""
        data = await self._create(URL_BASE, kwargs)
        return Account.model_validate(data)

    async def get(self, account_id: str) -> Account:
        """Retrieve a single account by ID."""
        data = await self._get(f"{URL_BASE}/{account_id}")
        return Account.model_validate(data)

    async def list(
        self,
        per_page: int = 50,
        offset: int = 0,
        limit: int = 0,
    ) -> list[Account]:
        """Return a full list of accounts, paginating internally."""
        if per_page not in range(1, 51):
            raise ValueError(
                "per_page must be between 1 and 50 (inclusive)"
            )

        if limit:
            per_page = min(per_page, limit)

        params: dict[str, Any] = {"limit": per_page, "offset": offset}
        result: list[Account] = []
        accounts: list[dict] = await self._list(URL_BASE, params=params)

        while accounts:
            for account in accounts:
                result.append(Account.model_validate(account))
                if limit and len(result) >= limit:
                    return result

            params["offset"] += per_page
            if limit and params["offset"] + per_page > limit:
                params["limit"] = limit - params["offset"]
            accounts = await self._list(URL_BASE, params=params)

        return result

    async def update(self, account_id: str, **kwargs: Any) -> Account:
        """Update an existing account."""
        data = await self._update(
            f"{URL_BASE}/{account_id}", kwargs, method="PATCH"
        )
        return Account.model_validate(data)

    async def delete(self, account_id: str) -> None:
        """Delete an account."""
        await self._delete(f"{URL_BASE}/{account_id}")
