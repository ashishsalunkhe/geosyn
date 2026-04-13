from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models.domain import MarketSeries, MarketPoint, EventCluster, Document, Alert
from app.ingestion.yahoo_market_provider import YahooMarketProvider
from app.services.sentiment_service import SentimentService
from app.core.tickers import ALL_TRACKED_TICKERS

import asyncio

class MarketService:
    def __init__(self, db: Session):
        self.db = db
        self.sentiment_service = SentimentService()

    async def sync_all_markets(self):
        """
        Fetches latest points for all tracked tickers and detects volatility shocks.
        """
        print(f"GeoSyn: Syncing {len(ALL_TRACKED_TICKERS)} tickers...")
        
        # To avoid rate limits, we process in chunks or rely on threaded calls
        for ticker_symbol in ALL_TRACKED_TICKERS:
            try:
                # 1. Get or Create Series
                series = self.db.query(MarketSeries).filter(MarketSeries.ticker == ticker_symbol).first()
                if not series:
                    series = MarketSeries(ticker=ticker_symbol, name=ticker_symbol, asset_class="equity")
                    self.db.add(series)
                    self.db.commit()
                    self.db.refresh(series)

                # 2. Fetch Latest Points
                provider = YahooMarketProvider(ticker_symbol)
                # Fetch 30 days of data to ensure enough points for the chart and trend analysis
                points_data = await asyncio.to_thread(provider.fetch_series, days=30)
                
                if not points_data:
                    continue

                # Detect Volatility for Alerting
                # Calculate % change between the last two available points (e.g., yesterday and today)
                if len(points_data) < 2:
                    continue
                    
                first_val = points_data[-2]["value"]
                last_val = points_data[-1]["value"]
                if first_val == 0:
                    continue
                change_pct = ((last_val - first_val) / first_val) * 100

                # Threshold: 2% move in a day (Typical for high-vol alerts)
                if abs(change_pct) > 2.0:
                    severity = "high" if abs(change_pct) > 5.0 else "medium"
                    
                    # Check for duplicate recent alerts to avoid spam
                    recent_alert = self.db.query(Alert).filter(
                        Alert.ticker == ticker_symbol,
                        Alert.created_at > datetime.utcnow() - timedelta(minutes=60)
                    ).first()

                    if not recent_alert:
                        from app.services.explainability_service import ExplainabilityService
                        explainer = ExplainabilityService(self.db)
                        
                        new_alert = Alert(
                            type="volatility",
                            severity=severity,
                            ticker=ticker_symbol,
                            title=f"Volatility Shock: ${ticker_symbol}",
                            content=f"Detected significant price velocity of {change_pct:+.2f}% in the current trading session.",
                            context_snippet=f"Market price for {ticker_symbol} shifted from {first_val:.2f} to {last_val:.2f}.",
                            alert_payload={"ticker": ticker_symbol, "change_pct": change_pct}
                        )
                        self.db.add(new_alert)
                        self.db.commit() # Commit to get ID
                        self.db.refresh(new_alert)
                        
                        # Enrich with explanation
                        explanation = explainer.explain_alert(new_alert.id)
                        new_alert.alert_payload["explanation"] = explanation
                        self.db.add(new_alert)

                # Save points
                for p in points_data:
                    ts = datetime.fromisoformat(p["timestamp"])
                    existing = self.db.query(MarketPoint).filter(
                        MarketPoint.series_id == series.id,
                        MarketPoint.timestamp == ts
                    ).first()
                    if not existing:
                        self.db.add(MarketPoint(
                            series_id=series.id,
                            timestamp=ts,
                            value=p["value"],
                            volume=p.get("volume")
                        ))
                
                self.db.commit()
            except Exception as e:
                # Silent skip for delisted/no-data to keep logs clean
                if "No data found" in str(e) or "delisted" in str(e).lower():
                    pass 
                else:
                    print(f"Error syncing {ticker_symbol}: {e}")
                self.db.rollback()

    async def sync_market_data(self):
        """Compatibility wrapper — delegates to sync_all_markets."""
        await self.sync_all_markets()

    def get_market_narrative_shocks(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Correlates market points with event clusters.
        """
        series = self.db.query(MarketSeries).filter(MarketSeries.ticker == ticker).first()
        if not series:
            return {"ticker": ticker, "points": [], "shocks": []}
            
        points = self.db.query(MarketPoint).filter(
            MarketPoint.series_id == series.id
        ).order_by(MarketPoint.timestamp.asc()).all()
        
        events = self.db.query(EventCluster).all()
        
        shocks = []
        for event in events:
            # Calculate intensity
            docs = self.db.query(Document).filter(Document.event_cluster_id == event.id).all()
            intensity = self.sentiment_service.get_event_intensity(event, docs)
            
            if intensity > 0.4: # Threshold for a 'shock'
                shocks.append({
                    "event_id": event.id,
                    "event_title": event.title,
                    "timestamp": event.created_at.isoformat(),
                    "intensity": intensity
                })
                
        return {
            "ticker": ticker,
            "points": [{"t": p.timestamp.isoformat(), "v": p.value} for p in points],
            "shocks": shocks
        }
