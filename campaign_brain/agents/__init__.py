"""
Campaign Brain Agents module
"""

from .trend_scout import TrendScout
from .strategist import Strategist
from .persona_simulator import PersonaSimulator
from .designer import Designer
from .executor import Executor

__all__ = [
    "TrendScout",
    "Strategist", 
    "PersonaSimulator",
    "Designer",
    "Executor"
]