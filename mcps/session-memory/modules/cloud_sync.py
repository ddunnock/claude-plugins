"""Cloud sync to Cloudflare D1 + R2.

This module provides optional cloud synchronization:
- D1 (SQLite) for structured data (events, entities, learnings)
- R2 (object storage) for checkpoints and large objects
- Conflict resolution with local-first priority

R2 Configuration:
    R2 uses S3-compatible API and requires separate credentials:
    - CF_R2_ACCESS_KEY_ID: R2 API token access key ID
    - CF_R2_SECRET_ACCESS_KEY: R2 API token secret access key

    Generate these at: Cloudflare Dashboard > R2 > Manage R2 API Tokens
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Optional dependencies
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import boto3
    from botocore.config import Config as BotoConfig
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class CloudSyncService:
    """Sync session data to Cloudflare D1 (SQLite) and R2 (objects)."""

    RESOURCE_TYPES = ["event", "checkpoint", "entity", "learning", "embedding"]

    def __init__(self, db_path: str, config: Dict[str, Any]):
        self.db_path = db_path
        self.enabled = config.get("enabled", False)

        # Load credentials from config or environment
        # Supports direct values, custom env var names via _env suffix, or default env vars
        self.account_id = (
            config.get("account_id") or
            os.environ.get(config.get("account_id_env", ""), "") or
            os.environ.get("CF_ACCOUNT_ID")
        )
        self.api_token = (
            config.get("api_token") or
            os.environ.get(config.get("api_token_env", ""), "") or
            os.environ.get("CF_API_TOKEN")
        )
        self.d1_database_id = (
            config.get("d1_database_id") or
            os.environ.get(config.get("d1_database_id_env", ""), "") or
            os.environ.get("CF_D1_DATABASE_ID")
        )
        self.r2_bucket = (
            config.get("r2_bucket") or
            os.environ.get(config.get("r2_bucket_env", ""), "") or
            os.environ.get("CF_R2_BUCKET")
        )

        # R2 S3-compatible credentials (separate from API token)
        self.r2_access_key_id = (
            config.get("r2_access_key_id") or
            os.environ.get(config.get("r2_access_key_id_env", ""), "") or
            os.environ.get("CF_R2_ACCESS_KEY_ID")
        )
        self.r2_secret_access_key = (
            config.get("r2_secret_access_key") or
            os.environ.get(config.get("r2_secret_access_key_env", ""), "") or
            os.environ.get("CF_R2_SECRET_ACCESS_KEY")
        )
        # R2 endpoint URL (can differ from main account_id)
        self.r2_endpoint_url = (
            config.get("r2_endpoint_url") or
            os.environ.get(config.get("r2_endpoint_url_env", ""), "") or
            os.environ.get("CF_R2_ENDPOINT_URL")
        )

        # Check availability
        self.available = (
            HTTPX_AVAILABLE and
            self.enabled and
            self.account_id and
            self.api_token
        )

        # R2 availability (requires boto3, R2 credentials, and endpoint)
        self.r2_available = (
            BOTO3_AVAILABLE and
            self.enabled and
            self.r2_endpoint_url and
            self.r2_bucket and
            self.r2_access_key_id and
            self.r2_secret_access_key
        )

        if self.available:
            self.client = httpx.Client(
                base_url=f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
        else:
            self.client = None

        # Initialize R2 S3 client
        if self.r2_available:
            self.r2_client = boto3.client(
                "s3",
                endpoint_url=self.r2_endpoint_url,
                aws_access_key_id=self.r2_access_key_id,
                aws_secret_access_key=self.r2_secret_access_key,
                config=BotoConfig(
                    signature_version="s3v4",
                    retries={"max_attempts": 3, "mode": "standard"}
                ),
                region_name="auto"  # R2 uses 'auto' region
            )
        else:
            self.r2_client = None

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_status(self) -> Dict[str, Any]:
        """Get cloud sync status."""
        if not self.enabled:
            return {
                "enabled": False,
                "available": False,
                "message": "Cloud sync not enabled in config"
            }

        if not self.available:
            missing = []
            if not HTTPX_AVAILABLE:
                missing.append("httpx library")
            if not self.account_id:
                missing.append("CF_ACCOUNT_ID")
            if not self.api_token:
                missing.append("CF_API_TOKEN")

            return {
                "enabled": True,
                "available": False,
                "message": f"Missing: {', '.join(missing)}"
            }

        conn = self._get_conn()
        try:
            # Count pending and conflict items
            pending_count = conn.execute(
                "SELECT COUNT(*) FROM sync_state WHERE sync_status = 'pending'"
            ).fetchone()[0]

            conflict_count = conn.execute(
                "SELECT COUNT(*) FROM sync_state WHERE sync_status = 'conflict'"
            ).fetchone()[0]

            synced_count = conn.execute(
                "SELECT COUNT(*) FROM sync_state WHERE sync_status = 'synced'"
            ).fetchone()[0]

            last_sync = conn.execute(
                "SELECT MAX(last_sync) FROM sync_state WHERE sync_status = 'synced'"
            ).fetchone()[0]

            # Build R2 status
            r2_status = {
                "available": self.r2_available,
                "bucket": self.r2_bucket,
                "endpoint": self.r2_endpoint_url
            }
            if not self.r2_available:
                r2_missing = []
                if not BOTO3_AVAILABLE:
                    r2_missing.append("boto3 library")
                if not self.r2_endpoint_url:
                    r2_missing.append("CF_R2_ENDPOINT_URL")
                if not self.r2_access_key_id:
                    r2_missing.append("CF_R2_ACCESS_KEY_ID")
                if not self.r2_secret_access_key:
                    r2_missing.append("CF_R2_SECRET_ACCESS_KEY")
                if r2_missing:
                    r2_status["missing"] = r2_missing

            return {
                "enabled": True,
                "available": True,
                "d1_database_id": self.d1_database_id,
                "r2": r2_status,
                "pending_count": pending_count,
                "conflict_count": conflict_count,
                "synced_count": synced_count,
                "last_sync": last_sync
            }
        finally:
            conn.close()

    def push(
        self,
        resource_types: Optional[List[str]] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """Push local changes to cloud."""
        if not self.available:
            return {"success": False, "error": "Cloud sync not available"}

        if not self.d1_database_id:
            return {"success": False, "error": "D1 database ID not configured"}

        resource_types = resource_types or self.RESOURCE_TYPES
        conn = self._get_conn()
        results = {"pushed": 0, "errors": [], "conflicts_resolved": 0}

        try:
            # Get pending items
            placeholders = ",".join("?" * len(resource_types))
            status_filter = "('pending', 'conflict')" if force else "('pending')"
            sql = f"SELECT * FROM sync_state WHERE sync_status IN {status_filter} AND resource_type IN ({placeholders})"  # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query
            rows = conn.execute(sql, resource_types).fetchall()  # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query

            for row in rows:
                try:
                    resource_type = row["resource_type"]
                    resource_id = row["resource_id"]

                    # Get the actual resource data
                    resource_data = self._get_resource_data(conn, resource_type, resource_id)
                    if not resource_data:
                        continue

                    # Push to D1
                    success = self._push_to_d1(resource_type, resource_data)

                    if success:
                        # Update sync state
                        conn.execute("""
                            UPDATE sync_state
                            SET sync_status = 'synced',
                                last_sync = ?,
                                local_version = local_version + 1,
                                remote_version = local_version + 1
                            WHERE id = ?
                        """, (datetime.now(datetime.UTC).isoformat(), row["id"]))
                        results["pushed"] += 1

                        if row["sync_status"] == "conflict":
                            results["conflicts_resolved"] += 1
                    else:
                        results["errors"].append(f"Failed to push {resource_type}:{resource_id}")

                except Exception as e:
                    results["errors"].append(f"Error pushing {row['resource_type']}:{row['resource_id']}: {str(e)}")

            conn.commit()
            results["success"] = len(results["errors"]) == 0

        finally:
            conn.close()

        return results

    def pull(
        self,
        resource_types: Optional[List[str]] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """Pull changes from cloud to local."""
        if not self.available:
            return {"success": False, "error": "Cloud sync not available"}

        if not self.d1_database_id:
            return {"success": False, "error": "D1 database ID not configured"}

        resource_types = resource_types or self.RESOURCE_TYPES
        results = {"pulled": 0, "errors": [], "conflicts": 0}

        try:
            for resource_type in resource_types:
                # Query D1 for remote data
                remote_data = self._query_d1(resource_type)

                if remote_data is None:
                    results["errors"].append(f"Failed to query {resource_type} from D1")
                    continue

                # Merge with local
                merge_result = self._merge_remote_data(resource_type, remote_data, force)
                results["pulled"] += merge_result["merged"]
                results["conflicts"] += merge_result["conflicts"]

            results["success"] = len(results["errors"]) == 0

        except Exception as e:
            results["errors"].append(str(e))
            results["success"] = False

        return results

    def _get_resource_data(
        self,
        conn: sqlite3.Connection,
        resource_type: str,
        resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get resource data from local database."""
        table_map = {
            "event": "events",
            "checkpoint": "checkpoints",
            "entity": "entities",
            "learning": "learnings",
            "embedding": "embeddings"
        }

        table = table_map.get(resource_type)
        if not table:
            return None

        # Table name from hardcoded allowlist (table_map), not user input
        sql = f"SELECT * FROM {table} WHERE id = ?"  # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query
        row = conn.execute(sql, (resource_id,)).fetchone()  # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query

        if row:
            return dict(row)
        return None

    def _push_to_d1(self, resource_type: str, data: Dict[str, Any]) -> bool:
        """Push a resource to D1 database."""
        if not self.client:
            return False

        try:
            # Build upsert SQL based on resource type
            if resource_type == "event":
                sql = """
                    INSERT OR REPLACE INTO events
                    (id, timestamp, category, type, session_id, parent_id, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = [
                    data["id"], data["timestamp"], data["category"],
                    data.get("type"), data["session_id"], data.get("parent_id"),
                    json.dumps(data.get("data", {}))
                ]
            elif resource_type == "learning":
                sql = """
                    INSERT OR REPLACE INTO learnings
                    (id, timestamp, category, title, description, context_hash,
                     source_session_ids, confidence, usage_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = [
                    data["id"], data["timestamp"], data["category"],
                    data["title"], data.get("description"), data.get("context_hash"),
                    data.get("source_session_ids"), data.get("confidence", 0.7),
                    data.get("usage_count", 0), data.get("metadata")
                ]
            elif resource_type == "entity":
                sql = """
                    INSERT OR REPLACE INTO entities
                    (id, type, name, qualified_name, first_seen_session, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                params = [
                    data["id"], data["type"], data["name"],
                    data.get("qualified_name"), data.get("first_seen_session"),
                    data.get("metadata")
                ]
            else:
                return False

            response = self.client.post(
                f"/d1/database/{self.d1_database_id}/query",
                json={"sql": sql, "params": params}
            )

            return response.status_code == 200 and response.json().get("success", False)

        except Exception:
            return False

    def _query_d1(self, resource_type: str) -> Optional[List[Dict]]:
        """Query resources from D1."""
        if not self.client:
            return None

        table_map = {
            "event": "events",
            "checkpoint": "checkpoints",
            "entity": "entities",
            "learning": "learnings"
        }

        table = table_map.get(resource_type)
        if not table:
            return None

        try:
            response = self.client.post(
                f"/d1/database/{self.d1_database_id}/query",
                json={"sql": f"SELECT * FROM {table}"}
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("result"):
                    return result["result"][0].get("results", [])

            return None

        except Exception:
            return None

    def _merge_remote_data(
        self,
        resource_type: str,
        remote_data: List[Dict],
        force: bool
    ) -> Dict[str, int]:
        """Merge remote data with local database."""
        conn = self._get_conn()
        result = {"merged": 0, "conflicts": 0}

        try:
            for remote_item in remote_data:
                item_id = remote_item.get("id")
                if not item_id:
                    continue

                # Check local sync state
                sync_row = conn.execute(
                    "SELECT * FROM sync_state WHERE resource_type = ? AND resource_id = ?",
                    (resource_type, item_id)
                ).fetchone()

                if sync_row:
                    remote_version = remote_item.get("_version", 1)
                    local_version = sync_row["local_version"]

                    if remote_version > local_version or force:
                        # Remote is newer or force merge
                        self._upsert_local(conn, resource_type, remote_item)
                        conn.execute("""
                            UPDATE sync_state
                            SET remote_version = ?, sync_status = 'synced', last_sync = ?
                            WHERE resource_type = ? AND resource_id = ?
                        """, (remote_version, datetime.now(datetime.UTC).isoformat(),
                              resource_type, item_id))
                        result["merged"] += 1
                    elif remote_version < local_version:
                        # Conflict - local is newer
                        if not force:
                            conn.execute("""
                                UPDATE sync_state
                                SET sync_status = 'conflict', conflict_data = ?
                                WHERE resource_type = ? AND resource_id = ?
                            """, (json.dumps(remote_item), resource_type, item_id))
                            result["conflicts"] += 1
                else:
                    # New remote item
                    self._upsert_local(conn, resource_type, remote_item)
                    conn.execute("""
                        INSERT INTO sync_state
                        (id, resource_type, resource_id, local_version, remote_version, sync_status, last_sync)
                        VALUES (?, ?, ?, 1, 1, 'synced', ?)
                    """, (
                        f"sync-{datetime.now(datetime.UTC).strftime('%Y%m%d%H%M%S%f')}",
                        resource_type, item_id, datetime.now(datetime.UTC).isoformat()
                    ))
                    result["merged"] += 1

            conn.commit()
        finally:
            conn.close()

        return result

    def _upsert_local(
        self,
        conn: sqlite3.Connection,
        resource_type: str,
        data: Dict[str, Any]
    ):
        """Insert or update a resource in local database."""
        # Implementation depends on resource type
        # This would use INSERT OR REPLACE for each table
        pass

    def mark_for_sync(
        self,
        resource_type: str,
        resource_id: str
    ):
        """Mark a resource as needing sync."""
        if not self.enabled:
            return

        conn = self._get_conn()
        try:
            # Check if already tracked
            existing = conn.execute(
                "SELECT id, local_version FROM sync_state WHERE resource_type = ? AND resource_id = ?",
                (resource_type, resource_id)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE sync_state
                    SET local_version = local_version + 1, sync_status = 'pending'
                    WHERE id = ?
                """, (existing["id"],))
            else:
                conn.execute("""
                    INSERT INTO sync_state
                    (id, resource_type, resource_id, local_version, sync_status)
                    VALUES (?, ?, ?, 1, 'pending')
                """, (
                    f"sync-{datetime.now(datetime.UTC).strftime('%Y%m%d%H%M%S%f')}",
                    resource_type, resource_id
                ))

            conn.commit()
        finally:
            conn.close()

    def upload_to_r2(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Upload an object to R2 bucket.

        Args:
            key: Object key (path) in the bucket
            data: Bytes to upload
            content_type: MIME type of the content
            metadata: Optional metadata dict to attach to the object

        Returns:
            True if upload succeeded, False otherwise
        """
        if not self.r2_available or not self.r2_client:
            return False

        try:
            put_kwargs: Dict[str, Any] = {
                "Bucket": self.r2_bucket,
                "Key": key,
                "Body": data,
                "ContentType": content_type
            }

            if metadata:
                put_kwargs["Metadata"] = metadata

            self.r2_client.put_object(**put_kwargs)
            return True

        except Exception:
            return False

    def download_from_r2(self, key: str) -> Optional[bytes]:
        """Download an object from R2 bucket.

        Args:
            key: Object key (path) in the bucket

        Returns:
            Object bytes if found, None otherwise
        """
        if not self.r2_available or not self.r2_client:
            return None

        try:
            response = self.r2_client.get_object(
                Bucket=self.r2_bucket,
                Key=key
            )
            return response["Body"].read()

        except self.r2_client.exceptions.NoSuchKey:
            return None
        except Exception:
            return None

    def delete_from_r2(self, key: str) -> bool:
        """Delete an object from R2 bucket.

        Args:
            key: Object key (path) in the bucket

        Returns:
            True if deletion succeeded, False otherwise
        """
        if not self.r2_available or not self.r2_client:
            return False

        try:
            self.r2_client.delete_object(
                Bucket=self.r2_bucket,
                Key=key
            )
            return True

        except Exception:
            return False

    def list_r2_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000
    ) -> Optional[List[Dict[str, Any]]]:
        """List objects in R2 bucket.

        Args:
            prefix: Filter objects by key prefix
            max_keys: Maximum number of objects to return

        Returns:
            List of object metadata dicts, or None on error
        """
        if not self.r2_available or not self.r2_client:
            return None

        try:
            response = self.r2_client.list_objects_v2(
                Bucket=self.r2_bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            objects = []
            for obj in response.get("Contents", []):
                objects.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                    "etag": obj.get("ETag", "").strip('"')
                })

            return objects

        except Exception:
            return None

    def upload_checkpoint_to_r2(self, checkpoint_id: str, checkpoint_data: Dict[str, Any]) -> bool:
        """Upload a checkpoint to R2 as JSON.

        Args:
            checkpoint_id: Checkpoint identifier
            checkpoint_data: Checkpoint data dict

        Returns:
            True if upload succeeded
        """
        key = f"checkpoints/{checkpoint_id}.json"
        data = json.dumps(checkpoint_data, indent=2).encode("utf-8")

        return self.upload_to_r2(
            key=key,
            data=data,
            content_type="application/json",
            metadata={"checkpoint_id": checkpoint_id}
        )

    def download_checkpoint_from_r2(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Download a checkpoint from R2.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Checkpoint data dict, or None if not found
        """
        key = f"checkpoints/{checkpoint_id}.json"
        data = self.download_from_r2(key)

        if data:
            try:
                return json.loads(data.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None

        return None
