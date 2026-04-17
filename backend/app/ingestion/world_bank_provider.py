import wbgapi as wb
from datetime import datetime
from typing import List, Dict, Any
from app.ingestion.base import BaseProvider
from app.utils.datalake_manager import datalake

class WorldBankProvider(BaseProvider):
    """
    Provider for World Bank macroeconomic and trade signals.
    Utilizes wbgapi to capture high-fidelity trade and energy volume data.
    """
    
    @property
    def provider_name(self) -> str:
        return "World Bank"

    @property
    def source_type(self) -> str:
        return "institutional_macro"

    # World Bank Core Indicators
    INDICATORS = {
        "NE.RSB.GNFS.ZS": "Trade Balance (% of GDP)",
        "TX.VAL.FUEL.ZS.UN": "Fuel Exports (% of Merchandise Exports)",
        "GC.DOD.TOTL.GD.ZS": "Central Government Debt (% of GDP)"
    }

    def fetch_raw_docs(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Queries World Bank indicators for global and regional anchors.
        """
        results = []
        
        for code, label in self.INDICATORS.items():
            try:
                print(f"WorldBank: Pulling Indicator {code} ({label})...")
                
                # Use fetch for a more stable record-based structure
                # mrv=1 gets the Most Recent Value
                records = list(wb.data.fetch(code, "WLD", mrv=1))
                
                if records:
                    rec = records[0]
                    # Persist raw representation to Data Lake
                    datalake.store_raw_signal("worldbank", rec, metadata={"indicator_code": code})
                    
                    latest_val = rec.get("value")
                    year_str = rec.get("time", "2023").replace("YR", "") # fallback to 2023 if time is missing
                    
                    if latest_val is not None:
                        results.append({
                            "id": f"wb-{code}-{year_str}",
                            "title": f"World Bank Indicator: {label}",
                            "content": f"World Bank reports {label} at {float(latest_val):.2f} for {year_str} (Global).",
                            "url": f"https://data.worldbank.org/indicator/{code}",
                            "published_at": datetime(int(year_str), 1, 1).isoformat(),
                            "source": self.provider_name,
                            "raw_val": float(latest_val),
                            "indicator_code": code
                        })
            except Exception as e:
                print(f"WorldBank Fetch Error [{code}]: {e}")
            except Exception as e:
                print(f"WorldBank Fetch Error [{code}]: {e}")
                
        return results
