import requests
from openai import OpenAI
from app.core.config import settings
from typing import List, Dict, Any, Optional
import json

class LLMService:
    """
    Handles high-level reasoning and synthesis tasks using OpenAI GPT models.
    Provides graceful fallback if no API key is present.
    """
    
    OLLAMA_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "llama3" # Defaulting to Llama-3

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.tavily_api_key = settings.TAVILY_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        # Check if local Ollama is reachable
        self.use_local = self._check_ollama()
        
        if self.use_local:
            print(f"LLM REASONING INITIALIZED: LOCAL (Ollama @ {self.OLLAMA_URL})")
        elif self.is_enabled_cloud:
            print(f"LLM REASONING INITIALIZED: CLOUD (OpenAI model: {self.model})")
        else:
            print("LLM REASONING INITIALIZED: MOCK MODE (No local or cloud model detected)")

    def _check_ollama(self) -> bool:
        """Heuristic check for local Ollama service."""
        try:
            # We check the tags endpoint to see if Ollama is up
            resp = requests.get("http://localhost:11434/api/tags", timeout=1)
            return resp.status_code == 200
        except:
            return False

    @property
    def is_enabled_cloud(self) -> bool:
        return self.client is not None

    @property
    def is_enabled(self) -> bool:
        return self.use_local or self.is_enabled_cloud

    def _call_llm(self, prompt: str, system_msg: str, mode: str = "json") -> Dict[str, Any]:
        """Centralized call handler that routes to Local or Cloud."""
        # 1. Try Local Ollama First
        if self.use_local:
            try:
                # Local models often don't support response_format="json_object" natively in the same way,
                # so we include strong formatting instructions in the prompt.
                full_prompt = f"SYSTEM: {system_msg}\n\nUSER: {prompt}\n\nIMPORTANT: Return ONLY valid JSON. No preamble."
                
                response = requests.post(self.OLLAMA_URL, json={
                    "model": self.OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "format": "json" if mode == "json" else None
                }, timeout=30)
                
                if response.status_code == 200:
                    text_out = response.json().get("response", "{}")
                    return json.loads(text_out)
            except Exception as e:
                print(f"Local LLM Error: {e}. Falling back...")

        # 2. Try OpenAI Cloud Fallback
        if self.is_enabled_cloud:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_msg},
                              {"role": "user", "content": prompt}],
                    response_format={"type": "json_object"} if mode == "json" else None
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Cloud LLM Error: {e}")

        # 3. Final Fallback: Mock Data (Enterprise Continuity)
        return self._generate_mock_response(prompt)

    def _search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a real-time tactical search via Tavily for LLM augmentation.
        """
        if not self.tavily_api_key:
            print("LLM Augmentation: Tavily API Key missing. Skipping search.")
            return []
            
        try:
            print(f"LLM Augmentation: Initiating Search-Augmented Pipeline for '{query}'...")
            resp = requests.post("https://api.tavily.com/search", json={
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": False,
                "max_results": 5
            }, timeout=10)
            
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                return [{"title": r.get("title"), "url": r.get("url"), "snippet": r.get("content")} for r in results]
        except Exception as e:
            print(f"Web Search Error: {e}")
            
        return []

    def synthesize_intelligence_brief(self, topic: str, articles: List[Dict[str, Any]], stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesizes raw news metadata into a local-first high-fidelity brief with optional Search Augmentation."""
        context_articles = articles[:5]
        
        # AGENTIC TRIGGER: If we have very few articles, augment with a live web search
        if len(context_articles) < 3 and topic:
            search_results = self._search_web(topic)
            for res in search_results:
                context_articles.append({
                    "title": f"[AUGMENTED] {res['title']}",
                    "source": "Web Intelligence",
                    "tone": 0, # Neutral placeholder
                    "url": res["url"]
                })

        context = {
            "topic": topic,
            "articles": [{"title": a.get("title"), "source": a.get("source"), "tone": a.get("tone")} for a in context_articles],
            "stats": stats
        }

        prompt = f"Synthesize these news signals (including augmented web data if present) into an intelligence brief: {json.dumps(context)}"
        system_msg = "You are a world-class geopolitical risk analyst. Return a JSON object with 'narrative_summary', 'causal_chain', 'market_projections', and 'strategic_outlook'."
        
        return self._call_llm(prompt, system_msg)

    def generate_causal_reasoning(self, alert_content: str, evidence_titles: List[str], correlation_pattern: Optional[str] = None) -> Dict[str, Any]:
        """Generates a strategic narrative explaining a specific market alert using local reasoning."""
        prompt = f"Analyze this alert: {alert_content}. Evidence: {', '.join(evidence_titles)}. Pattern: {correlation_pattern}"
        system_msg = "Explain the causal link between news and price moves. Return JSON with 'strategic_narrative', 'historical_context', and 'confidence_score'."
        
        return self._call_llm(prompt, system_msg)

    def _generate_mock_response(self, prompt: str) -> Dict[str, Any]:
        """High-fidelity mock generator for local testing without active models."""
        return {
            "narrative_summary": "Initial intelligence suggests a significant alignment between reported events and current market volatility.",
            "causal_chain": [{"step": 1, "event": "Regional Tension", "inference": "Reduced risk appetite in local equities"}],
            "market_projections": [
                {"asset": "Brent Crude", "ticker": "CL=F", "category": "COMMODITY", "direction": "UP", "magnitude": "MODERATE", "rationale": "Supply disruption risk", "confidence_score": 0.75, "justification": "Direct news coverage"}
            ],
            "strategic_outlook": "Monitor for further escalation in the 24-48h window.",
            "strategic_narrative": "The observed price action correlates with specific risk keywords in the GDELT stream.",
            "historical_context": "Similar patterns observed in 2022 regional conflicts.",
            "confidence_score": 0.65
        }
