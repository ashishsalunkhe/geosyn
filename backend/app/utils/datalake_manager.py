import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings


class DataLakeManager:
    """
    Object-storage aware raw signal manager.

    Default behavior uses local filesystem storage under `OBJECT_STORAGE_LOCAL_PATH`,
    but the same interface can target S3-compatible object storage when configured.
    """

    def __init__(self, base_path: str | None = None):
        self.provider = settings.OBJECT_STORAGE_PROVIDER.lower()
        self.bucket = settings.OBJECT_STORAGE_BUCKET
        self.base_path = Path(base_path or settings.OBJECT_STORAGE_LOCAL_PATH)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.curated_path = self.base_path / "curated"

        if self.provider == "local":
            for path in [self.raw_path, self.processed_path, self.curated_path]:
                path.mkdir(parents=True, exist_ok=True)

    def store_raw_signal(self, source: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        now = datetime.utcnow()
        object_key = self._build_object_key(source, now)
        payload = {
            "ingested_at": now.isoformat(),
            "source": source,
            "metadata": metadata or {},
            "data": data,
        }

        if self.provider == "local":
            return self._store_local(object_key, payload)
        return self._store_remote(object_key, payload)

    def list_raw_signals(self, source: str, date: Optional[datetime] = None) -> list[str]:
        if self.provider != "local":
            prefix = self._build_prefix(source, date)
            return [f"s3://{self.bucket}/{prefix}"]

        search_path = self.raw_path / source
        if date:
            search_path = search_path / date.strftime("%Y") / date.strftime("%m") / date.strftime("%d")
        if not search_path.exists():
            return []
        return [str(path) for path in search_path.glob("**/*.json")]

    def _store_local(self, object_key: str, payload: Dict[str, Any]) -> str:
        target_file = self.base_path / object_key
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        return str(target_file)

    def _store_remote(self, object_key: str, payload: Dict[str, Any]) -> str:
        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=settings.OBJECT_STORAGE_ENDPOINT_URL,
            region_name=settings.OBJECT_STORAGE_REGION,
            aws_access_key_id=settings.OBJECT_STORAGE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.OBJECT_STORAGE_SECRET_ACCESS_KEY,
            use_ssl=settings.OBJECT_STORAGE_USE_SSL,
        )
        client.put_object(
            Bucket=self.bucket,
            Key=object_key,
            Body=json.dumps(payload).encode("utf-8"),
            ContentType="application/json",
        )
        return f"s3://{self.bucket}/{object_key}"

    @staticmethod
    def _build_prefix(source: str, date: Optional[datetime] = None) -> str:
        if date:
            return f"raw/{source}/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"
        return f"raw/{source}"

    @staticmethod
    def _build_object_key(source: str, dt: datetime) -> str:
        return (
            f"raw/{source}/{dt.strftime('%Y')}/{dt.strftime('%m')}/{dt.strftime('%d')}/"
            f"{dt.strftime('%H%M%S_%f')}.json"
        )


datalake = DataLakeManager()
