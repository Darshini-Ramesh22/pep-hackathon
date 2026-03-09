"""
Strategist Agent - Develops comprehensive campaign strategy
"""
import json
import sys
import os
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class Strategist:
    """
    Agent responsible for developing comprehensive campaign strategy
    based on trends, objectives, and constraints.
    """
    
    def __init__(self):
        self.client = Config.get_openai_client()
        self.model = Config.MODEL_NAME
        
    def develop_strategy(
        self,
        objective: str,
        trends: List[Dict[str, Any]],
        competitor_analysis: Dict[str, Any],
        budget: float,
        duration: int
    ) -> Dict[str, Any]:
        """
        Develop comprehensive campaign strategy
        
        Args:
            objective (str): Campaign objective
            trends (List): Current market trends
            competitor_analysis (Dict): Competitor analysis results
            budget (float): Available budget
            duration (int): Campaign duration in days
            
        Returns:
            Dict containing strategy, messaging, channels, and metrics
        """
        
        # Load strategist prompt
        with open("campaign_brain/prompts/strategist_prompt.txt", "r") as f:
            prompt_template = f.read()
            
        # Prepare trend summary
        trend_summary = "\n".join([
            f"- {trend.get('name', 'Unknown')}: {trend.get('impact', 'medium')} impact"
            for trend in trends[:5]
        ])
        
        # Prepare competitor insights
        competitor_summary = "\n".join([
            f"- {strategy}" for strategy in 
            competitor_analysis.get("strategies", [])[:3]
        ])
        
        # Prepare the prompt
        prompt = prompt_template.format(
            objective=objective,
            budget=f"${budget:,.2f}",
            duration=duration,
            trends=trend_summary,
            competitors=competitor_summary,
            opportunities="\n".join([
                f"- {opp}" for opp in 
                competitor_analysis.get("opportunities", [])[:3]
            ])
        )
        
        try:
            # Call the AI model
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior marketing strategist specializing in FMCG brand campaigns. "
                            "Respond with ONLY a valid JSON object — no markdown, no backticks, no extra text. "
                            "Use this exact structure: "
                            '{"strategy": "2-3 sentence summary of the core campaign approach", '
                            '"key_messages": ["message 1", "message 2", "message 3"], '
                            '"channels": [{"name": "string", "budget_allocation": number, "expected_reach": number}], '
                            '"metrics": ["metric 1", "metric 2"]}. '
                            "Keep strategy concise and action-oriented. Recommend 3-5 channels with realistic budget splits. "
                            "Do not include any text outside the JSON object."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            # Parse the response
            strategy_text = response.choices[0].message.content
            
            # Extract structured strategy
            strategy = self._parse_strategy(strategy_text, budget, duration)
            with open("campaign_brain/logs/strategist_response.txt", "w") as f:
                f.write(strategy_text)
            
            return strategy
            
        except Exception as e:
            print(f"Error in strategy development: {str(e)}")
            return self._get_fallback_strategy(budget, duration)
    
    def _parse_strategy(
        self,
        strategy_text: str,
        budget: float,
        duration: int
    ) -> Dict[str, Any]:
        """Parse the AI response into structured strategy."""

        import re

        def _finalise(data: Dict) -> Dict:
            if not data.get("channels"):
                data["channels"] = self._get_default_channels(budget)
            if not data.get("key_messages"):
                data["key_messages"] = ["Clear value proposition", "Brand differentiation", "Call-to-action"]
            if not data.get("metrics"):
                data["metrics"] = ["Reach", "Engagement rate", "Conversion rate", "ROAS"]
            n = len(data["channels"])
            for ch in data["channels"]:
                ch.setdefault("budget_allocation", round(budget / n, 2))
                ch.setdefault("expected_reach", int(ch["budget_allocation"] * 100))
            return data

        # ── 1. Direct JSON parse ──────────────────────────────────────────
        try:
            data = json.loads(strategy_text.strip())
            if isinstance(data, dict) and "strategy" in data:
                return _finalise(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # ── 2. Strip markdown fences then parse ──────────────────────────
        try:
            cleaned = re.sub(r"```(?:json)?|```", "", strategy_text).strip()
            data = json.loads(cleaned)
            if isinstance(data, dict) and "strategy" in data:
                return _finalise(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # ── 3. Extract outermost { } block ───────────────────────────────
        try:
            start = strategy_text.find("{")
            end = strategy_text.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(strategy_text[start:end])
                if isinstance(data, dict) and "strategy" in data:
                    return _finalise(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # ── 4. Plain-text fallback ────────────────────────────────────────
        return self._get_fallback_strategy(budget, duration)
    
    def _get_default_channels(self, budget: float) -> List[Dict[str, Any]]:
        """Get default channel recommendations based on budget"""
        
        if budget < 10000:
            return [
                {"name": "Social Media Organic", "budget_allocation": budget * 0.4, "expected_reach": 5000},
                {"name": "Email Marketing", "budget_allocation": budget * 0.3, "expected_reach": 2000},
                {"name": "Content Marketing", "budget_allocation": budget * 0.3, "expected_reach": 3000}
            ]
        elif budget < 50000:
            return [
                {"name": "Social Media Paid", "budget_allocation": budget * 0.35, "expected_reach": 25000},
                {"name": "Google Ads", "budget_allocation": budget * 0.25, "expected_reach": 15000},
                {"name": "Email Marketing", "budget_allocation": budget * 0.2, "expected_reach": 10000},
                {"name": "Content Marketing", "budget_allocation": budget * 0.2, "expected_reach": 12000}
            ]
        else:
            return [
                {"name": "TV/Video Advertising", "budget_allocation": budget * 0.3, "expected_reach": 100000},
                {"name": "Social Media Paid", "budget_allocation": budget * 0.25, "expected_reach": 80000},
                {"name": "Google Ads", "budget_allocation": budget * 0.2, "expected_reach": 60000},
                {"name": "Influencer Partnerships", "budget_allocation": budget * 0.15, "expected_reach": 40000},
                {"name": "Email Marketing", "budget_allocation": budget * 0.1, "expected_reach": 30000}
            ]
    
    def _get_fallback_strategy(self, budget: float, duration: int) -> Dict[str, Any]:
        """Provide fallback strategy if AI call fails"""
        return {
            "strategy": f"Multi-channel integrated campaign approach over {duration} days, focusing on digital-first engagement with measurable ROI targets.",
            "key_messages": [
                "Clear value proposition highlighting unique benefits",
                "Emotional connection with target audience",
                "Strong call-to-action driving desired behavior",
                "Brand consistency across all touchpoints"
            ],
            "channels": self._get_default_channels(budget),
            "metrics": [
                "Reach and frequency",
                "Engagement rate",
                "Click-through rate", 
                "Conversion rate",
                "Cost per acquisition",
                "Return on advertising spend",
                "Brand awareness lift"
            ]
        }