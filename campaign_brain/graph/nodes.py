"""
Agent nodes for the Campaign Brain workflow
"""
import sys
import os
import traceback
from typing import Dict, Any

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .state import CampaignState
from agents.trend_scout import TrendScout
from agents.strategist import Strategist
from agents.persona_simulator import PersonaSimulator
from agents.designer import Designer
from agents.executor import Executor


def trend_scout_node(state: CampaignState) -> CampaignState:
    """
    Trend Scout agent node - analyzes current trends and market insights
    """
    print("🔍 Trend Scout is analyzing market trends...")
    
    try:
        trend_scout = TrendScout()
        
        # Update state with current agent
        state["current_agent"] = "trend_scout"
        
        # Run trend analysis
        trends = trend_scout.analyze_trends(
            objective=state["campaign_objective"],
            target_audience=state["target_audience"],
            budget=state["budget"]
        )
        
        # Validate structure
        if not isinstance(trends, dict):
            print("⚠️  TrendScout returned invalid structure, using fallback")
            trends = trend_scout._get_fallback_trends()
        
        # Update state with results
        state["current_trends"] = trends.get("trends", [])
        state["competitor_analysis"] = trends.get("competitor_analysis", {})
        state["market_insights"] = trends.get("market_insights", [])
        
        # Ensure all are proper types
        if not isinstance(state["current_trends"], list):
            state["current_trends"] = []
        if not isinstance(state["competitor_analysis"], dict):
            state["competitor_analysis"] = {}
        if not isinstance(state["market_insights"], list):
            state["market_insights"] = []
        
        # Mark agent as completed and set next agent
        if "trend_scout" not in state["completed_agents"]:
            state["completed_agents"].append("trend_scout")
        state["next_agent"] = "strategist"
        
        print(f"✅ Trend Scout completed analysis - {len(state['current_trends'])} trends identified")
        return state
        
    except Exception as e:
        print(f"❌ Error in trend_scout_node: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Return state with fallback values - don't fail the workflow
        state["current_trends"] = []
        state["competitor_analysis"] = {}
        state["market_insights"] = []
        
        if "trend_scout" not in state["completed_agents"]:
            state["completed_agents"].append("trend_scout")
        state["next_agent"] = "strategist"
        
        print("⚠️  TrendScout failed but workflow continuing with empty trends...")
        return state


def strategist_node(state: CampaignState) -> CampaignState:
    """
    Strategist agent node - develops campaign strategy based on trends
    """
    print("🎯 Strategist is developing campaign strategy...")
    
    strategist = Strategist()
    
    # Update state with current agent
    state["current_agent"] = "strategist"
    
    # Develop strategy
    strategy = strategist.develop_strategy(
        objective=state["campaign_objective"],
        trends=state["current_trends"],
        competitor_analysis=state["competitor_analysis"],
        budget=state["budget"],
        duration=state["duration_days"]
    )
    
    # Update state with results
    state["campaign_strategy"] = strategy.get("strategy", "")
    state["key_messaging"] = strategy.get("key_messages", [])
    state["channel_recommendations"] = strategy.get("channels", [])
    state["success_metrics"] = strategy.get("metrics", [])
    
    # Mark agent as completed and set next agent
    if "strategist" not in state["completed_agents"]:
        state["completed_agents"].append("strategist")
    state["next_agent"] = "persona_simulator"
    
    print("✅ Strategist completed strategy development")
    return state


def persona_simulator_node(state: CampaignState) -> CampaignState:
    """
    Persona Simulator agent node - creates detailed user personas and journey maps
    """
    print("👥 Persona Simulator is creating user personas...")
    
    persona_simulator = PersonaSimulator()
    
    # Update state with current agent
    state["current_agent"] = "persona_simulator"
    
    # Create personas
    personas = persona_simulator.create_personas(
        target_audience=state["target_audience"],
        strategy=state["campaign_strategy"],
        trends=state["current_trends"]
    )
    
    # Update state with results
    state["persona_profiles"] = personas.get("personas", [])
    state["user_journey_maps"] = personas.get("journey_maps", [])
    state["pain_points"] = personas.get("pain_points", [])
    state["motivation_drivers"] = personas.get("motivations", [])
    
    # Mark agent as completed and set next agent
    if "persona_simulator" not in state["completed_agents"]:
        state["completed_agents"].append("persona_simulator")
    state["next_agent"] = "designer"
    
    print("✅ Persona Simulator completed persona creation")
    return state


def designer_node(state: CampaignState) -> CampaignState:
    """
    Designer agent node - creates creative concepts and visual guidelines
    """
    print("🎨 Designer is creating creative concepts...")
    
    designer = Designer()
    
    # Update state with current agent
    state["current_agent"] = "designer"
    
    # Create designs
    creative_output = designer.create_concepts(
        strategy=state["campaign_strategy"],
        personas=state["persona_profiles"],
        brand_guidelines=state["brand_guidelines"],
        channels=state["channel_recommendations"]
    )
    
    # Update state with results
    state["creative_concepts"] = creative_output.get("concepts", [])
    state["visual_guidelines"] = creative_output.get("visual_guidelines", "")
    state["content_ideas"] = creative_output.get("content_ideas", [])
    
    # Mark agent as completed and set next agent
    if "designer" not in state["completed_agents"]:
        state["completed_agents"].append("designer")
    state["next_agent"] = "executor"
    
    print("✅ Designer completed creative development")
    return state


def executor_node(state: CampaignState) -> CampaignState:
    """
    Executor agent node - creates implementation plan and timeline
    """
    print("⚡ Executor is creating implementation plan...")
    
    executor = Executor()
    
    # Update state with current agent
    state["current_agent"] = "executor"
    
    # Create execution plan
    execution_plan = executor.create_execution_plan(
        strategy=state["campaign_strategy"],
        creative_concepts=state["creative_concepts"],
        channels=state["channel_recommendations"],
        budget=state["budget"],
        duration=state["duration_days"]
    )
    
    # Update state with results
    state["campaign_timeline"] = execution_plan.get("timeline", {})
    state["resource_allocation"] = execution_plan.get("resources", {})
    state["implementation_steps"] = execution_plan.get("steps", [])
    state["risk_mitigation"] = execution_plan.get("risks", [])
    
    # Create final campaign plan
    state["final_campaign_plan"] = {
        "objective": state["campaign_objective"],
        "strategy": state["campaign_strategy"],
        "personas": state["persona_profiles"],
        "creative_concepts": state["creative_concepts"],
        "timeline": state["campaign_timeline"],
        "budget_allocation": state["resource_allocation"],
        "implementation": state["implementation_steps"],
        "success_metrics": state["success_metrics"],
        "risks": state["risk_mitigation"]
    }
    
    # Mark agent as completed and workflow as ready
    if "executor" not in state["completed_agents"]:
        state["completed_agents"].append("executor")
    state["next_agent"] = None
    state["presentation_ready"] = True
    
    print("✅ Executor completed implementation planning")
    print("🎉 Campaign Brain workflow completed!")
    return state


def should_continue(state: CampaignState) -> str:
    """
    Router function to determine next agent or end workflow
    """
    if state["next_agent"]:
        return state["next_agent"]
    else:
        return "END"