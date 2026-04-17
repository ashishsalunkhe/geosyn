import os
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

class DataLakeManager:
    """
    Manages the local simulation of an AWS S3 Data Lake.
    Persists raw signals in a structured directory format: 
    data/raw/{source}/{year}/{month}/{day}/{timestamp}.json
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Default to the 'data' directory in the project root
            self.base_path = Path(__file__).parent.parent.parent.parent / "data"
        else:
            self.base_path = Path(base_path)
            
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.curated_path = self.base_path / "curated"
        
        # Ensure directories exist
        for p in [self.raw_path, self.processed_path, self.curated_path]:
            p.mkdir(parents=True, exist_ok=True)

    def store_raw_signal(self, source: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Stores a raw API response to the Data Lake.
        Returns the path to the stored file.
        """
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        timestamp = now.strftime("%H%M%S_%f")
        
        target_dir = self.raw_path / source / year / month / day
        target_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{timestamp}.json"
        target_file = target_dir / filename
        
        payload = {
            "ingested_at": now.isoformat(),
            "source": source,
            "metadata": metadata or {},
            "data": data
        }
        
        with open(target_file, "w") as f:
            json.dump(payload, f, indent=2)
            
        return str(target_file)

    def list_raw_signals(self, source: str, date: Optional[datetime] = None) -> list:
        """
        List paths to stored signals for a given source and optional date.
        """
        search_path = self.raw_path / source
        if date:
            search_path = search_path / date.strftime("%Y") / date.strftime("%m") / date.strftime("%d")
            
        if not search_path.exists():
            return []
            
        return [str(p) for p in search_path.glob("**/*.json")]

datalake = DataLakeManager()
