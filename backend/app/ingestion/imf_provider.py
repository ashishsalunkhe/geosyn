import requests
import json
from datetime import datetime
from typing import List, Dict, Any
from app.ingestion.base import BaseProvider
from app.utils.datalake_manager import datalake

class IMFProvider(BaseProvider):
    """
    Provider for IMF (International Monetary Fund) DataMapper signals.
    Captures Global Growth, Inflation, and systemic Debt levels.
    """
    
    @property
    def provider_name(self) -> str:
        return "IMF DataMapper"

    @property
    def source_type(self) -> str:
        return "institutional_macro"

    # IMF DataMapper Indicators
    INDICATORS = {
        "NGDP_RPCH": "Real GDP Growth (%)",
        "PCPIPCH": "Inflation Rate (%)",
        "BCA_NGDPD": "Current Account Balance (% of GDP)",
        "DEBT_GDP": "Total Debt-to-GDP (%)"
    }

    def fetch_raw_docs(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Fetches macroeconomic indicators and persists them to the Data Lake.
        """
        results = []
        base_url = "https://www.imf.org/external/datamapper/api/v1"
        
        for code, label in self.INDICATORS.items():
            try:
                print(f"IMF: Pulling Indicator {code} ({label})...")
                url = f"{base_url}/{code}"
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Persist to Data Lake
                    datalake.store_raw_signal("imf", data, metadata={"indicator_code": code})
                    
                    # Extract the most recent data point for the Global average or specific regions
                    # IMF response structure: {"values": {"INDICATOR_CODE": {"REGION": {"YEAR": VALUE}}}}
                    values = data.get("values", {}).get(code, {})
                    
                    # Focus on "World" (Global) indicator if present
                    global_data = values.get("World", {})
                    if global_data:
                        # Get latest year
                        latest_year = max(global_data.keys(), key=int)
                        latest_val = global_data[latest_year]
                        
                        results.append({
                            "id": f"imf-{code}-{latest_year}",
                            "title": f"IMF Global Indicator: {label}",
                            "content": f"The IMF reports {label} at {latest_val} for {latest_year} (Global).",
                            "url": url,
                            "published_at": datetime(int(latest_year), 1, 1).isoformat(),
                            "source": self.provider_name,
                            "raw_val": latest_val,
                            "indicator_code": code
                        })
            except Exception as e:
                print(f"IMF Fetch Error [{code}]: {e}")
                
        return results
