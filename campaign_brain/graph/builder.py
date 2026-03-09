"""
LangGraph builder for Campaign Brain workflow
"""
from langgraph.graph import StateGraph, START, END
from .state import CampaignState
from .nodes import (
    trend_scout_node,
    strategist_node,
    persona_simulator_node,
    designer_node,
    executor_node,
    should_continue
)


def create_campaign_brain_graph():
    """
    Creates and returns the Campaign Brain workflow graph
    """
    # Initialize the graph
    workflow = StateGraph(CampaignState)
    
    # Add agent nodes
    workflow.add_node("trend_scout", trend_scout_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("persona_simulator", persona_simulator_node)
    workflow.add_node("designer", designer_node)
    workflow.add_node("executor", executor_node)
    
    # Set entry point
    workflow.set_entry_point("trend_scout")
    
    # Add conditional edges based on router function
    workflow.add_conditional_edges(
        "trend_scout",
        should_continue,
        {
            "strategist": "strategist",
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "strategist", 
        should_continue,
        {
            "persona_simulator": "persona_simulator",
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "persona_simulator",
        should_continue,
        {
            "designer": "designer", 
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "designer",
        should_continue,
        {
            "executor": "executor",
            "END": END
        }
    )
    
    workflow.add_conditional_edges(
        "executor",
        should_continue,
        {
            "END": END
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    return app


def run_campaign_brain(
    campaign_objective: str,
    target_audience: str,
    budget: float,
    duration_days: int = 30,
    brand_guidelines: str = ""
):
    """
    Convenience function to run the complete Campaign Brain workflow
    
    Args:
        campaign_objective (str): The main goal of the campaign
        target_audience (str): Description of the target audience
        budget (float): Campaign budget
        duration_days (int): Campaign duration in days
        brand_guidelines (str): Brand guidelines and constraints
        
    Returns:
        CampaignState: Final state with complete campaign plan
    """
    
    # Create the graph
    app = create_campaign_brain_graph()
    
    # Initialize state
    initial_state = CampaignState(
        campaign_objective=campaign_objective,
        target_audience=target_audience,
        budget=budget,
        duration_days=duration_days,
        brand_guidelines=brand_guidelines,
        current_agent="",
        completed_agents=[],
        iteration_count=0
    )
    
    print("🚀 Starting Campaign Brain workflow...")
    print(f"Objective: {campaign_objective}")
    print(f"Target Audience: {target_audience}")
    print(f"Budget: ${budget:,.2f}")
    print(f"Duration: {duration_days} days")
    print("-" * 50)
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    return final_state