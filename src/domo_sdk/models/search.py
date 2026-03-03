"""Search models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class SearchEntity(str, Enum):
    """Searchable entity types."""

    DATASET = "DATASET"
    USER = "USER"
    CARD = "CARD"
    DATAFLOW = "DATAFLOW"
    APP = "APP"
    ACCOUNT = "ACCOUNT"
    ALERT = "ALERT"
    PAGE = "PAGE"
    PROJECT = "PROJECT"
    BUZZ_CHANNEL = "BUZZ_CHANNEL"


class SearchQuery(DomoModel):
    """Search query parameters."""

    query: str = "*"
    count: int = 50
    offset: int = 0
    entities: list[SearchEntity] = Field(default_factory=list)
    filters: list[dict[str, Any]] = Field(default_factory=list)
    combine_results: bool = Field(default=True, alias="combineResults")
    sort: dict[str, Any] | None = None


class SearchResult(DomoModel):
    """Individual search result."""

    id: str = ""
    name: str = ""
    type: str = ""
    description: str = ""
    owner: dict[str, Any] | None = None


class SearchResponse(DomoModel):
    """Search response containing results."""

    data_sources: list[SearchResult] = Field(default_factory=list, alias="dataSources")
    users: list[SearchResult] = Field(default_factory=list)
    cards: list[SearchResult] = Field(default_factory=list)
    total_count: int = Field(default=0, alias="totalCount")
