"""S3 export models."""

from __future__ import annotations

from pydantic import Field

from domo_sdk.models.base import DomoModel


class S3Export(DomoModel):
    """S3 export status."""

    export_id: str = Field(default="", alias="exportId")
    dataset_id: str = Field(default="", alias="datasetId")
    status: str = ""
    s3_key: str = Field(default="", alias="s3Key")
