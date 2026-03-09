"""
Campaign Brain - AI-Powered Multi-Agent Campaign Planning System

A sophisticated system that uses multiple AI agents working together
to create comprehensive marketing campaign plans.

Components:
- Trend Scout: Market trend analysis
- Strategist: Campaign strategy development
- Persona Simulator: Audience insight generation
- Designer: Creative concept creation
- Executor: Implementation planning

Usage:
    from campaign_brain import run_campaign_brain
    
    results = run_campaign_brain(
        campaign_objective="Your campaign goal",
        target_audience="Your target audience",
        budget=50000,
        duration_days=30
    )
"""

from .graph.builder import run_campaign_brain, create_campaign_brain_graph
from .config import Config

__version__ = "1.0.0"
__author__ = "Campaign Brain Team"

__all__ = [
    "run_campaign_brain",
    "create_campaign_brain_graph", 
    "Config"
]