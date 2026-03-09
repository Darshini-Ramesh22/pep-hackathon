"""
Graph State definition for Campaign Brain workflow
"""
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import MessagesState

class CampaignState(MessagesState):
    """
    State structure for the Campaign Brain multi-agent workflow
    """
    
    # Campaign Brief
    campaign_objective: str = ""
    target_audience: str = ""
    budget: float = 0.0
    duration_days: int = 30
    brand_guidelines: str = ""
    
    # Trend Scout Results
    current_trends: List[Dict[str, Any]] = []
    competitor_analysis: Dict[str, Any] = {}
    market_insights: List[str] = []
    
    # Strategic Planning
    campaign_strategy: str = ""
    key_messaging: List[str] = []
    channel_recommendations: List[Dict[str, Any]] = []
    success_metrics: List[str] = []
    
    # Persona Insights
    persona_profiles: List[Dict[str, Any]] = []
    user_journey_maps: List[Dict[str, Any]] = []
    pain_points: List[str] = []
    motivation_drivers: List[str] = []
    
    # Creative Design
    creative_concepts: List[Dict[str, Any]] = []
    visual_guidelines: str = ""
    content_ideas: List[Dict[str, Any]] = []
    
    # Execution Plan
    campaign_timeline: Dict[str, Any] = {}
    resource_allocation: Dict[str, Any] = {}
    implementation_steps: List[Dict[str, Any]] = []
    risk_mitigation: List[str] = []
    
    # Workflow Control
    current_agent: str = ""
    completed_agents: List[str] = []
    next_agent: Optional[str] = None
    iteration_count: int = 0
    
    # Analysis and Feedback
    analysis_results: Dict[str, Any] = {}
    feedback_scores: Dict[str, float] = {}
    improvement_suggestions: List[str] = []
    
    # Final Output
    final_campaign_plan: Dict[str, Any] = {}
    presentation_ready: bool = False