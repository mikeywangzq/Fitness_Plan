"""
User API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserOnboarding, UserUpdate
from typing import List

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    """
    # TODO: Implement user creation with password hashing
    # This is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User creation not yet implemented"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user.
    """
    # TODO: Implement authentication and get current user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented"
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.
    """
    # TODO: Implement user update
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User update not yet implemented"
    )


@router.post("/me/onboarding", response_model=UserResponse)
async def complete_onboarding(
    onboarding_data: UserOnboarding,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete user onboarding by setting fitness goals and profile.
    Implements FR-1: 用户引导与目标设定
    """
    # TODO: Implement onboarding completion
    # - Update user profile with onboarding data
    # - Set onboarding_completed = True
    # - Generate initial workout and nutrition plans
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Onboarding not yet implemented"
    )


@router.get("/me/profile")
async def get_user_profile(
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive user profile including goals and preferences.
    """
    # TODO: Return complete user profile
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile retrieval not yet implemented"
    )
