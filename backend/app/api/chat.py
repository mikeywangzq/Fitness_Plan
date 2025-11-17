"""
Chat API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, OnboardingResponse
from app.agents.fitness_agent import FitnessAgent
from app.agents.workout_planner import WorkoutPlannerAgent
from app.agents.nutrition_planner import NutritionPlannerAgent
from app.agents.progress_analyzer import ProgressAnalyzerAgent
from typing import Dict, Any
import uuid

router = APIRouter()

# Initialize agents (in production, use dependency injection)
fitness_agent = FitnessAgent()
workout_agent = WorkoutPlannerAgent()
nutrition_agent = NutritionPlannerAgent()
progress_agent = ProgressAnalyzerAgent()

# Simple in-memory storage for conversations (in production, use database)
conversations: Dict[str, list] = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the fitness agent and get a response.
    """
    try:
        # Get or create conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Get conversation history
        chat_history = conversations.get(conversation_id, [])

        # TODO: Get user context from database
        user_context = {
            # This should be fetched from database based on authenticated user
            # For now, using placeholder
        }

        # Get response from agent
        response = await fitness_agent.chat(
            message=request.message,
            user_context=user_context,
            chat_history=chat_history if request.include_history else None
        )

        # Store messages in conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        conversations[conversation_id].append({
            "role": "user",
            "content": request.message
        })
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response
        })

        # Analyze intent
        intent_data = await fitness_agent.analyze_intent(request.message)

        return ChatResponse(
            message=response,
            conversation_id=conversation_id,
            intent=intent_data.get("intent"),
            metadata=intent_data.get("extracted_info")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/onboarding", response_model=OnboardingResponse)
async def onboarding_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Special endpoint for user onboarding conversation.
    Helps users set up their profile and goals.
    """
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        chat_history = conversations.get(conversation_id, [])

        # Create onboarding-specific prompt
        onboarding_context = {
            "mode": "onboarding",
            "step": len(chat_history) // 2  # Rough estimate of conversation step
        }

        response = await fitness_agent.chat(
            message=request.message,
            user_context=onboarding_context,
            chat_history=chat_history if request.include_history else None
        )

        # Store messages
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        conversations[conversation_id].append({
            "role": "user",
            "content": request.message
        })
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response
        })

        # Check if onboarding is complete (simplified logic)
        onboarding_complete = len(chat_history) > 10  # Example threshold

        return OnboardingResponse(
            message=response,
            onboarding_complete=onboarding_complete,
            next_steps=["创建训练计划", "设置营养目标"] if onboarding_complete else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear a conversation history.
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation cleared"}

    raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation history.
    """
    if conversation_id in conversations:
        return {
            "conversation_id": conversation_id,
            "messages": conversations[conversation_id]
        }

    raise HTTPException(status_code=404, detail="Conversation not found")
