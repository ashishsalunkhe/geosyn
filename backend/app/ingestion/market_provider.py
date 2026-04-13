from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

class MockMarketProvider:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def fetch_series(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Generates mock time series data for a ticker.
        """
        points = []
        base_price = {"CL=F": 80.0, "ES=F": 5000.0, "GC=F": 2000.0}.get(self.ticker, 100.0)
        
        current_time = datetime.utcnow() - timedelta(days=days)
        price = base_price

        for i in range(days * 24): # Hourly points
            current_time += timedelta(hours=1)
            # Random walk with slight upward bias
            price += random.uniform(-0.5, 0.6)
            points.append({
                "timestamp": current_time.isoformat(),
                "value": round(price, 2),
                "volume": random.randint(1000, 5000)
            })
            
        return points

    def fetch_assets(self) -> List[Dict[str, Any]]:
        return [
            {"ticker": "CL=F", "name": "Crude Oil Brent", "asset_class": "Commodity"},
            {"ticker": "ES=F", "name": "S&P 500 Futures", "asset_class": "Index"},
            {"ticker": "GC=F", "name": "Gold Futures", "asset_class": "Commodity"}
        ]
