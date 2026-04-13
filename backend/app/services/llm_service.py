from openai import OpenAI
from app.core.config import settings
from typing import List, Dict, Any, Optional
import json

class LLMService:
    """
    Handles high-level reasoning and synthesis tasks using OpenAI GPT models.
    Provides graceful fallback if no API key is present.
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        if self.is_enabled:
            print(f"LLM REASONING INITIALIZED: ACTIVE (model: {self.model})")
        else:
            print("LLM REASONING INITIALIZED: INACTIVE (No API Key found in .env)")

    @property
    def is_enabled(self) -> bool:
        return self.client is not None

    def synthesize_intelligence_brief(self, topic: str, articles: List[Dict[str, Any]], stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synthesizes raw news metadata and correlation stats into a high-fidelity brief.
        """
        if not self.is_enabled:
            return {}

        # Prepare context for LLM
        context = {
            "topic": topic,
            "articles": [{"title": a.get("title"), "source": a.get("source"), "tone": a.get("tone"), "themes": a.get("themes")[:3]} for a in articles],
            "stats": stats
        }

        prompt = f"""
        You are a Tactical Intelligence Officer. Synthesize the following news and market signals into a high-fidelity intelligence brief.
        
        {json.dumps(context, indent=2)}
        
        Return a JSON object with:
        - "narrative_summary": A 2-3 sentence strategic summary of the situation.
        - "causal_chain": A list of steps (max 5) explaining how these events lead to market effects. Each step has "step", "event", and "inference".
        - "market_projections": A detailed list of EXACTLY 10 assets to watch: MUST contain AT LEAST 5 specific company stocks (category: EQUITY) and AT LEAST 5 specific commodities (category: COMMODITY). Each item has:
            - "asset": Name of the asset (e.g. Brent Crude, Lockheed Martin).
            - "ticker": Ticker symbol if known (e.g. CL=F, LMT).
            - "category": [EQUITY, COMMODITY].
            - "direction": [UP, DOWN].
            - "magnitude": [HIGH, MODERATE, LOW].
            - "rationale": 1-sentence explanation of the link.
            - "confidence_score": (0.0 to 1.0) based on how directly the articles support this inference.
            - "justification": Short explanation of the confidence (e.g. "Directly mentioned in multiple sources").
        - "strategic_outlook": A single-sentence projection.
        
        Be precise, tactical, and brief. Verify all inferences against the thematic metadata provided.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a world-class geopolitical risk analyst."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Error (Brief): {e}")
            return {}

    def generate_causal_reasoning(self, alert_content: str, evidence_titles: List[str], correlation_pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a strategic narrative explaining a specific market alert.
        """
        if not self.is_enabled:
            return {}

        prompt = f"""
        Analyze this market alert and synthesize with the provided news evidence.
        
        Alert: {alert_content}
        Evidence: {", ".join(evidence_titles)}
        Pattern Match: {correlation_pattern}
        
        Return a JSON object with:
        - "strategic_narrative": A clear, concise explanation of the causal link between the news and this price move.
        - "historical_context": If possible, relate this to typical geopolitical market reactions.
        - "confidence_score": 0-1 scale.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You provide explainable AI reasoning for market intelligence."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Error (Reasoning): {e}")
            return {}
