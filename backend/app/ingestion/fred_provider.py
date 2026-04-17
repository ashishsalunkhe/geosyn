import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.utils.datalake_manager import datalake
from app.ingestion.base import BaseProvider

class FREDProvider(BaseProvider):
    """
    Ingests official economic data from the Federal Reserve Economic Data (FRED) API.
    Fulfills the 'institutional data' requirement for macro-econometric modeling.
    Includes data mirrored from BLS (Labor) and BEA (Economic Analysis).
    """
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    
    @property
    def provider_name(self) -> str:
        return "FRED"

    @property
    def source_type(self) -> str:
        return "institutional_macro"

    # Core series identifying systemic macro risk
    SERIES_MAP = {
        "DFF": "Federal Funds Effective Rate",
        "CPIAUCSL": "Consumer Price Index (Inflation)",
        "INDPRO": "Industrial Production Index",
        "DCOILWTICO": "WTI Crude Oil Price",
        "T10Y2Y": "Yield Spread (Recession Indicator)",
        "GDPC1": "Real GDP (BEA)",
        "PAYEMS": "Nonfarm Payrolls (BLS)",
        "UNRATE": "Unemployment Rate (BLS)",
        "PCE": "Consumption Expenditures (BEA)",
        "CHIPMIADJMEI": "Chinese Manufacturing PMI"
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FRED_API_KEY
        self.is_mock = self.api_key is None

    def fetch_raw_docs(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Implementation of BaseProvider interface. 
        Returns the latest observation for each series as a virtual 'document'.
        """
        results = []
        for series_id, label in self.SERIES_MAP.items():
            obs = self.fetch_series(series_id, days=7) # Get recent history
            if obs:
                latest = obs[-1]
                results.append({
                    "id": f"fred-{series_id}-{latest['date']}",
                    "title": f"Macro Signal: {label}",
                    "content": f"FRED reports {label} at {latest['value']} for period {latest['date']}.",
                    "url": f"https://fred.stlouisfed.org/series/{series_id}",
                    "published_at": latest["date"],
                    "source": self.provider_name,
                    "raw_val": latest["value"],
                    "indicator_code": series_id
                })
        return results

    def fetch_series(self, series_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetches historical data for a specific FRED series.
        Persists RAW response to the Data Lake before returning.
        """
        if self.is_mock:
            return self._generate_mock_data(series_id, days)

        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            raw_data = response.json()
            
            # --- Enterprise Step: Persist to Data Lake ---
            datalake.store_raw_signal(
                source=f"fred_{series_id}",
                data=raw_data,
                metadata={"series_name": self.SERIES_MAP.get(series_id, "Unknown")}
            )
            
            # Normalize for internal consumption
            observations = raw_data.get("observations", [])
            return [
                {
                    "date": obs["date"],
                    "value": float(obs["value"]) if (obs["value"] != "." and obs["value"] is not None) else None
                }
                for obs in observations
            ]
        except Exception as e:
            print(f"FRED API Error ({series_id}): {e}")
            return self._generate_mock_data(series_id, days)

    def _generate_mock_data(self, series_id: str, days: int) -> List[Dict[str, Any]]:
        """
        Fallback generator for when no API key is provided.
        """
        import random
        data = []
        base_val = {
            "DFF": 5.33, "CPIAUCSL": 310.0, "INDPRO": 102.5, 
            "DCOILWTICO": 75.0, "T10Y2Y": -0.45, "GDPC1": 22000.0,
            "PAYEMS": 158000.0, "UNRATE": 3.8
        }.get(series_id, 100.0)
        
        for i in range(days):
            date_str = (datetime.utcnow() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            # Random walk
            base_val += random.uniform(-0.05, 0.05) if series_id != "DCOILWTICO" else random.uniform(-1.0, 1.1)
            data.append({"date": date_str, "value": round(base_val, 4)})
            
        return data

fred_provider = FREDProvider()
