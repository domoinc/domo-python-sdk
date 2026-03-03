"""Page models."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class PageCollection(DomoModel):
    """Page collection (group of cards)."""

    id: int | None = None
    title: str = ""
    description: str = ""
    card_ids: list[int] = Field(default_factory=list, alias="cardIds")


class Page(DomoModel):
    """Page response from API."""

    id: int = 0
    name: str = ""
    parent_id: int = Field(default=0, alias="parentId")
    locked: bool = False
    owner_id: int = Field(default=0, alias="ownerId")
    card_ids: list[int] = Field(default_factory=list, alias="cardIds")
    visibility: dict[str, Any] | None = None
    collection_ids: list[int] = Field(
        default_factory=list, alias="collectionIds"
    )
    children: list[Page] = Field(default_factory=list)
