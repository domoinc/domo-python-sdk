"""Dataset models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from domo_sdk.models.base import DomoModel


class ColumnType(str, Enum):
    STRING = "STRING"
    DECIMAL = "DECIMAL"
    LONG = "LONG"
    DOUBLE = "DOUBLE"
    DATE = "DATE"
    DATETIME = "DATETIME"


class Column(DomoModel):
    """Dataset column definition."""

    type: ColumnType
    name: str


class Schema(DomoModel):
    """Dataset schema."""

    columns: list[Column] = Field(default_factory=list)


class UpdateMethod(str, Enum):
    APPEND = "APPEND"
    REPLACE = "REPLACE"


class Sorting(str, Enum):
    CARD_COUNT = "cardCount"
    NAME = "name"
    STATUS = "errorState"
    UPDATED = "lastUpdated"


class FilterOperator(str, Enum):
    EQUALS = "EQUALS"
    LIKE = "LIKE"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN_EQUAL = "GREATER_THAN_EQUAL"
    LESS_THAN_EQUAL = "LESS_THAN_EQUAL"
    BETWEEN = "BETWEEN"
    BEGINS_WITH = "BEGINS_WITH"
    ENDS_WITH = "ENDS_WITH"
    CONTAINS = "CONTAINS"


class PolicyFilter(DomoModel):
    """PDP policy filter."""

    column: str
    values: list[str] = Field(default_factory=list)
    operator: FilterOperator
    not_: bool = Field(default=False, alias="not")


class PolicyType(str, Enum):
    USER = "user"
    SYSTEM = "system"


class Policy(DomoModel):
    """Personalized Data Policy."""

    id: int | None = None
    type: PolicyType = PolicyType.USER
    name: str
    filters: list[PolicyFilter] = Field(default_factory=list)
    users: list[int] = Field(default_factory=list)
    virtual_users: list[int] = Field(default_factory=list, alias="virtualUsers")
    groups: list[int] = Field(default_factory=list)


class DataSetRequest(DomoModel):
    """Request to create/update a dataset."""

    name: str
    description: str = ""
    schema: Schema | None = None
    owner: dict[str, Any] | None = None


class DataSet(DomoModel):
    """Dataset response from API."""

    id: str = ""
    name: str = ""
    description: str = ""
    rows: int = 0
    columns: int = 0
    schema: Schema | None = None
    owner: dict[str, Any] | None = None
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
    data_current_at: datetime | None = Field(
        default=None, alias="dataCurrentAt"
    )
    pdp_enabled: bool = Field(default=False, alias="pdpEnabled")


class QueryResult(DomoModel):
    """SQL query result."""

    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    num_rows: int = Field(default=0, alias="numRows")
    num_columns: int = Field(default=0, alias="numColumns")


class DataSetPermission(DomoModel):
    """Dataset permission entry."""

    id: int
    type: str  # "USER" or "GROUP"
    permissions: list[str] = Field(default_factory=list)


class DataVersion(DomoModel):
    """Dataset data version."""

    version_id: str = Field(default="", alias="versionId")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    row_count: int = Field(default=0, alias="rowCount")


class Partition(DomoModel):
    """Dataset partition info."""

    partition_id: str = Field(default="", alias="partitionId")
    name: str = ""


class Index(DomoModel):
    """Dataset index."""

    columns: list[str] = Field(default_factory=list)


class UploadSession(DomoModel):
    """Dataset upload session."""

    upload_id: int = Field(default=0, alias="uploadId")


class SharePermission(DomoModel):
    """Permission entry for sharing a dataset."""

    id: int
    type: str  # "USER" or "GROUP"
    access_level: str = Field(default="READ", alias="accessLevel")
