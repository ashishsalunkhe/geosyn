import yfinance as yf
from typing import List, Dict, Any
from datetime import datetime, timedelta

class YahooMarketProvider:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def fetch_series(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetches real historical market data from Yahoo Finance.
        """
        try:
            # yfinance expects different ticker formats for some global indices
            # Sensex is ^BSESN, Nifty is ^NSEI
            ticker_obj = yf.Ticker(self.ticker)
            history = ticker_obj.history(period=f"{days}d", interval="1h")
            
            points = []
            for timestamp, row in history.iterrows():
                points.append({
                    "timestamp": timestamp.isoformat(),
                    "value": round(float(row["Close"]), 2),
                    "volume": float(row["Volume"]) if "Volume" in row else 0.0
                })
            return points
        except Exception as e:
            print(f"Error fetching data for {self.ticker}: {e}")
            return []

    def fetch_assets(self) -> List[Dict[str, Any]]:
        """
        Returns the major global indices requested by the user.
        """
        return [
            {"ticker": "^BSESN", "name": "BSE SENSEX", "asset_class": "Index"},
            {"ticker": "^NSEI", "name": "NIFTY 50", "asset_class": "Index"},
            {"ticker": "^GSPC", "name": "S&P 500", "asset_class": "Index"},
            {"ticker": "CL=F", "name": "Crude Oil Brent", "asset_class": "Commodity"},
            {"ticker": "GC=F", "name": "Gold Spot", "asset_class": "Commodity"},
            {"ticker": "^FTSE", "name": "FTSE 100", "asset_class": "Index"},
            {"ticker": "^N225", "name": "Nikkei 225", "asset_class": "Index"}
        ]
