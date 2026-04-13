import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.ingestion.gdelt_gkg_provider import GDELTGKGProvider
from app.ingestion.yahoo_market_provider import YahooMarketProvider

class CorrelationService:
    """
    Computes statistical correlation (Pearson r) between narrative volume and asset prices.
    Includes lag analysis to detect leading indicators.
    """
    
    def __init__(self):
        self.gkg_provider = GDELTGKGProvider()

    def compute_narrative_market_correlation(
        self, topic: str, ticker: str, window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculates Pearson correlation between topic volume and asset returns over a window.
        """
        # 1. Fetch GDELT Timeline Volume
        # GDELT returns a list of points: {"datetime": "...", "value": ...}
        timeline_data = self.gkg_provider.fetch_timeline_volume(topic, days=window_days)
        if not timeline_data:
            return {"error": "No timeline data found for topic"}

        # 2. Fetch Market Data
        market_provider = YahooMarketProvider(ticker)
        market_data = market_provider.fetch_series(days=window_days)
        if not market_data:
            return {"error": "No market data found for ticker"}

        # 3. Align and Normalize
        # We'll group by date to align timeline (news) and market (price)
        # News data is often hourly or daily; market is hourly or daily.
        # We index by date string 'YYYY-MM-DD' for simplicity in correlation.
        
        narrative_series = {}
        for p in timeline_data:
            # GDELT dates are often flexible strings or datetime objects
            dt_str = p.get("datetime", "")[:10] # Extract YYYY-MM-DD
            narrative_series[dt_str] = narrative_series.get(dt_str, 0) + p.get("value", 0)

        market_series = {}
        for p in market_data:
            dt_str = p.get("timestamp", "")[:10]
            # Use 'value' (Close price)
            market_series[dt_str] = p.get("value", 0)

        # Find common dates
        common_dates = sorted(list(set(narrative_series.keys()) & set(market_series.keys())))
        if len(common_dates) < 5:
            return {"error": "Insufficient overlapping data points", "sample_size": len(common_dates)}

        x = np.array([narrative_series[d] for d in common_dates])
        y = np.array([market_series[d] for d in common_dates])

        # We correlate narrative volume (x) with price returns (percent change of y)
        # or just price for simple trend analysis. Let's use log returns if possible, 
        # but simple values are easier for user explainability.
        
        # 4. Lag Analysis (0 to 3 days lag)
        results = []
        for lag in range(4):
            if len(x) - lag < 5:
                continue
            
            # Narrative (x) leads Market (y) by 'lag' days
            if lag == 0:
                current_x = x
                current_y = y
            else:
                current_x = x[:-lag]
                current_y = y[lag:]
            
            r, p_val = stats.pearsonr(current_x, current_y)
            results.append({
                "lag_days": lag,
                "r": round(float(r), 4),
                "p_value": round(float(p_val), 4),
                "is_significant": p_val < 0.05
            })

        # Find the "Best Fit" (highest absolute r)
        best_fit = sorted(results, key=lambda res: abs(res["r"]), reverse=True)[0] if results else None

        return {
            "topic": topic,
            "ticker": ticker,
            "window": f"{window_days} days",
            "sample_size": len(common_dates),
            "best_fit": best_fit,
            "all_lags": results
        }
