"""
AI Agents for fitness planning.
"""
from app.agents.fitness_agent import FitnessAgent
from app.agents.workout_planner import WorkoutPlannerAgent
from app.agents.nutrition_planner import NutritionPlannerAgent
from app.agents.progress_analyzer import ProgressAnalyzerAgent

__all__ = [
    "FitnessAgent",
    "WorkoutPlannerAgent",
    "NutritionPlannerAgent",
    "ProgressAnalyzerAgent",
]
