"""DataSet client for the Domo API."""

from __future__ import annotations

import os
from collections.abc import Generator
from typing import Any

from domo_sdk.clients.base import DomoAPIClient
from domo_sdk.models.datasets import (
    DataSet,
    DataSetPermission,
    DataVersion,
    Index,
    Partition,
    Policy,
    QueryResult,
    Schema,
    SharePermission,
    UploadSession,
)

URL_BASE = "/v1/datasets"


class DataSetClient(DomoAPIClient):
    """Manage Domo DataSets.

    Use DataSets for fairly static data sources that only require
    occasional updates via data replacement.  Use Streams if your
    data source is massive, constantly changing, or rapidly growing.

    Docs: https://developer.domo.com/docs/data-apis/data
    """

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(self, dataset_request: dict) -> DataSet:
        """Create a new DataSet."""
        data = self._create(URL_BASE, dataset_request)
        return DataSet.model_validate(data)

    def get(self, dataset_id: str) -> DataSet:
        """Retrieve a single DataSet by ID."""
        url = f"{URL_BASE}/{dataset_id}"
        data = self._get(url)
        return DataSet.model_validate(data)

    def list(
        self,
        sort: str | None = None,
        per_page: int = 50,
        offset: int = 0,
        limit: int = 0,
        name_like: str = "",
    ) -> Generator[DataSet, None, None]:
        """Paginating generator over DataSets.

        Yields individual DataSet models.  The Domo API enforces a max
        of 50 results per page; *per_page* is clamped accordingly.
        If *limit* is non-zero the generator stops after that many items.
        """
        if per_page not in range(1, 51):
            raise ValueError("per_page must be between 1 and 50 (inclusive)")

        if limit:
            per_page = min(per_page, limit)

        params: dict[str, Any] = {
            "limit": per_page,
            "offset": offset,
            "nameLike": name_like,
        }
        if sort is not None:
            params["sort"] = sort

        dataset_count = 0
        datasets: list[dict] = self._list(URL_BASE, params=params)

        while datasets:
            for dataset in datasets:
                yield DataSet.model_validate(dataset)
                dataset_count += 1
                if limit and dataset_count >= limit:
                    return

            params["offset"] += per_page
            if limit and params["offset"] + per_page > limit:
                params["limit"] = limit - params["offset"]
            datasets = self._list(URL_BASE, params=params)

    def update(self, dataset_id: str, dataset_update: dict) -> DataSet:
        """Update an existing DataSet."""
        url = f"{URL_BASE}/{dataset_id}"
        data = self._update(url, dataset_update)
        return DataSet.model_validate(data)

    def delete(self, dataset_id: str) -> None:
        """Delete a DataSet."""
        url = f"{URL_BASE}/{dataset_id}"
        self._delete(url)

    # ------------------------------------------------------------------
    # Data import / export
    # ------------------------------------------------------------------

    def data_import(
        self,
        dataset_id: str,
        csv_data: str,
        update_method: str = "REPLACE",
    ) -> None:
        """Import data from a CSV string."""
        url = f"{URL_BASE}/{dataset_id}/data?updateMethod={update_method}"
        self._upload_csv(url, csv_data.encode("utf-8"))

    def data_import_from_file(
        self,
        dataset_id: str,
        filepath: str,
        update_method: str = "REPLACE",
    ) -> None:
        """Import data from a CSV file on disk."""
        with open(os.path.expanduser(filepath), "rb") as csvfile:
            url = (
                f"{URL_BASE}/{dataset_id}/data"
                f"?updateMethod={update_method}"
            )
            self._upload_csv(url, csvfile.read())

    def data_export(
        self,
        dataset_id: str,
        include_csv_header: bool = True,
    ) -> str:
        """Export DataSet data as a CSV string."""
        url = f"{URL_BASE}/{dataset_id}/data"
        return self._download_csv(url, include_header=include_csv_header)

    def data_export_to_file(
        self,
        dataset_id: str,
        file_path: str,
        include_csv_header: bool = True,
    ) -> str:
        """Export DataSet data to a CSV file. Returns the file path."""
        csv_data = self.data_export(
            dataset_id, include_csv_header=include_csv_header
        )
        file_path = str(file_path)
        if not file_path.endswith(".csv"):
            file_path += ".csv"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(csv_data)
        return file_path

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(self, dataset_id: str, sql: str) -> QueryResult:
        """Execute a SQL query against a DataSet."""
        url = f"{URL_BASE}/query/execute/{dataset_id}"
        data = self._create(url, {"sql": sql})
        return QueryResult.model_validate(data)

    # ------------------------------------------------------------------
    # Schema & metadata (internal/v2/v3 APIs)
    # ------------------------------------------------------------------

    def get_schema(self, dataset_id: str) -> Schema:
        """Get the latest schema for a DataSet."""
        url = f"/data/v2/datasources/{dataset_id}/schemas/latest"
        data = self._get(url)
        return Schema.model_validate(data)

    def get_metadata(self, dataset_id: str) -> DataSet:
        """Get core metadata for a DataSet."""
        url = f"/data/v3/datasources/{dataset_id}"
        data = self._get(url, params={"part": "core"})
        return DataSet.model_validate(data)

    def alter_schema(self, dataset_id: str, schema: dict) -> Schema:
        """Create or alter the schema for a DataSet."""
        url = f"/data/v2/datasources/{dataset_id}/schemas"
        data = self._create(url, schema)
        return Schema.model_validate(data)

    # ------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------

    def get_permissions(self, dataset_id: str) -> list[DataSetPermission]:
        """Get permissions for a DataSet."""
        url = f"/data/v3/datasources/{dataset_id}/permissions"
        data = self._get(url)
        return [DataSetPermission.model_validate(p) for p in data]

    def set_permissions(self, dataset_id: str, permissions: list) -> None:
        """Set (replace) permissions for a DataSet."""
        url = f"/data/v3/datasources/{dataset_id}/permissions"
        self._update(url, permissions)

    def share(
        self,
        dataset_id: str,
        permissions: list[SharePermission | dict],
        send_email: bool = False,
    ) -> None:
        """Share a DataSet with users or groups.

        Args:
            dataset_id: The DataSet ID.
            permissions: List of SharePermission or dicts with id, type,
                accessLevel.
            send_email: Whether to send notification emails.
        """
        url = f"/data/v3/datasources/{dataset_id}/share"
        entries = [
            p.model_dump(by_alias=True) if isinstance(p, SharePermission) else p
            for p in permissions
        ]
        self._create(url, {"permissions": entries, "sendEmail": send_email})

    def revoke_access(self, dataset_id: str, user_id: int) -> None:
        """Revoke a user's access to a DataSet."""
        url = f"/data/v3/datasources/{dataset_id}/permissions/USER/{user_id}"
        self._delete(url)

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    def set_tags(self, dataset_id: str, tags: list[str]) -> None:
        """Set tags on a DataSet (replaces existing tags)."""
        url = f"/data/ui/v3/datasources/{dataset_id}/tags"
        self._create(url, tags)

    # ------------------------------------------------------------------
    # Versions & indexes
    # ------------------------------------------------------------------

    def list_versions(self, dataset_id: str) -> list[DataVersion]:
        """List data version details for a DataSet."""
        url = f"/data/v3/datasources/{dataset_id}/dataversions/details"
        data = self._get(url)
        return [DataVersion.model_validate(v) for v in data]

    def create_index(self, dataset_id: str, columns: list[str]) -> Index:
        """Create an index on the specified columns."""
        url = f"/data/v3/datasources/{dataset_id}/indexes"
        data = self._create(url, columns)
        return Index.model_validate(data)

    # ------------------------------------------------------------------
    # Partitions
    # ------------------------------------------------------------------

    def list_partitions(self, dataset_id: str) -> list[Partition]:
        """List partitions for a DataSet."""
        url = f"/api/query/v1/datasources/{dataset_id}/partition"
        data = self._get(url)
        return [Partition.model_validate(p) for p in data]

    def delete_partition(
        self, dataset_id: str, partition_id: str
    ) -> None:
        """Delete a partition tag from a DataSet."""
        url = (
            f"/api/query/v1/datasources/{dataset_id}"
            f"/partition/{partition_id}"
        )
        self._delete(url)

    # ------------------------------------------------------------------
    # Upload sessions (multi-part upload)
    # ------------------------------------------------------------------

    def create_upload_session(
        self,
        dataset_id: str,
        action: str = "REPLACE",
        partition_tag: str | None = None,
    ) -> UploadSession:
        """Create an upload session for multi-part data loading.

        Args:
            dataset_id: The DataSet ID.
            action: "REPLACE" or "APPEND".
            partition_tag: Optional partition tag for partitioned uploads.

        Returns:
            UploadSession with the upload_id.
        """
        url = f"/data/v3/datasources/{dataset_id}/uploads"
        params: dict[str, str] = {}
        if partition_tag:
            params["restateDataTag"] = partition_tag
        body: dict[str, Any] = {"action": action}
        data = self.transport.post(url, body=body, params=params or None)
        return UploadSession.model_validate(data)

    def upload_part(
        self,
        dataset_id: str,
        upload_id: int,
        part_number: int,
        csv_data: str | bytes,
    ) -> None:
        """Upload a CSV data part for a multi-part upload session."""
        url = (
            f"/data/v3/datasources/{dataset_id}"
            f"/uploads/{upload_id}/parts/{part_number}"
        )
        if isinstance(csv_data, str):
            csv_data = csv_data.encode("utf-8")
        self._upload_csv(url, csv_data)

    def commit_upload(
        self,
        dataset_id: str,
        upload_id: int,
        action: str = "REPLACE",
        index: bool = True,
        partition_tag: str | None = None,
    ) -> None:
        """Commit an upload session and trigger indexing.

        Args:
            dataset_id: The DataSet ID.
            upload_id: The upload session ID.
            action: "REPLACE" or "APPEND".
            index: Whether to trigger indexing after commit.
            partition_tag: Optional partition tag for partitioned commits.
        """
        url = (
            f"/data/v3/datasources/{dataset_id}"
            f"/uploads/{upload_id}/commit"
        )
        body: dict[str, Any] = {"action": action, "index": index}
        if partition_tag:
            body["restateDataTag"] = partition_tag
        self._update(url, body)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    def set_properties(
        self, dataset_id: str, properties: dict
    ) -> None:
        """Update DataSet properties (e.g., dataProviderType)."""
        url = f"/data/v3/datasources/{dataset_id}/properties"
        self._update(url, properties)

    # ------------------------------------------------------------------
    # PDP (Personalized Data Policies)
    # ------------------------------------------------------------------

    def create_pdp(self, dataset_id: str, pdp_request: dict) -> Policy:
        """Create a Personalized Data Policy."""
        url = f"{URL_BASE}/{dataset_id}/policies"
        data = self._create(url, pdp_request)
        return Policy.model_validate(data)

    def get_pdp(self, dataset_id: str, policy_id: int) -> Policy:
        """Get a specific PDP for a DataSet."""
        url = f"{URL_BASE}/{dataset_id}/policies/{policy_id}"
        data = self._get(url)
        return Policy.model_validate(data)

    def list_pdps(self, dataset_id: str) -> list[Policy]:
        """List all PDPs for a DataSet."""
        url = f"{URL_BASE}/{dataset_id}/policies"
        data = self._list(url)
        return [Policy.model_validate(p) for p in data]

    def update_pdp(
        self,
        dataset_id: str,
        policy_id: int,
        policy_update: dict,
    ) -> Policy:
        """Update a specific PDP for a DataSet."""
        url = f"{URL_BASE}/{dataset_id}/policies/{policy_id}"
        data = self._update(url, policy_update)
        return Policy.model_validate(data)

    def delete_pdp(self, dataset_id: str, policy_id: int) -> None:
        """Delete a specific PDP for a DataSet."""
        url = f"{URL_BASE}/{dataset_id}/policies/{policy_id}"
        self._delete(url)
