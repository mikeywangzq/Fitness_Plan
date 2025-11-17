"""
User schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import FitnessGoal, ExperienceLevel, EquipmentAccess


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserOnboarding(BaseModel):
    """Schema for user onboarding data."""
    age: Optional[int] = Field(None, ge=10, le=100)
    gender: Optional[str] = None
    height: Optional[float] = Field(None, gt=0)
    weight: Optional[float] = Field(None, gt=0)
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)

    fitness_goal: Optional[FitnessGoal] = None
    experience_level: Optional[ExperienceLevel] = ExperienceLevel.BEGINNER
    equipment_access: Optional[EquipmentAccess] = EquipmentAccess.BODYWEIGHT
    training_frequency: Optional[int] = Field(3, ge=1, le=7)

    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None

    target_weight: Optional[float] = None
    target_body_fat: Optional[float] = None
    goal_timeframe: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for user updates."""
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None

    fitness_goal: Optional[FitnessGoal] = None
    experience_level: Optional[ExperienceLevel] = None
    equipment_access: Optional[EquipmentAccess] = None
    training_frequency: Optional[int] = None

    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None

    target_weight: Optional[float] = None
    target_body_fat: Optional[float] = None
    goal_timeframe: Optional[int] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None

    fitness_goal: Optional[FitnessGoal] = None
    experience_level: Optional[ExperienceLevel] = None
    equipment_access: Optional[EquipmentAccess] = None
    training_frequency: Optional[int] = None

    target_weight: Optional[float] = None
    target_body_fat: Optional[float] = None
    goal_timeframe: Optional[int] = None

    is_active: bool
    onboarding_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload schema."""
    user_id: Optional[int] = None
