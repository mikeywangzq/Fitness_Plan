"""
User model.
"""
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class FitnessGoal(str, enum.Enum):
    """Fitness goal types."""
    MUSCLE_GAIN = "muscle_gain"
    FAT_LOSS = "fat_loss"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"
    BODY_RECOMPOSITION = "body_recomposition"


class ExperienceLevel(str, enum.Enum):
    """User experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EquipmentAccess(str, enum.Enum):
    """Available equipment types."""
    GYM = "gym"
    HOME = "home"
    BODYWEIGHT = "bodyweight"
    MINIMAL = "minimal"


class User(Base):
    """User model representing a fitness planner user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Profile Information
    full_name = Column(String(255))
    age = Column(Integer)
    gender = Column(String(20))

    # Body Metrics
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    body_fat_percentage = Column(Float, nullable=True)

    # Fitness Profile
    fitness_goal = Column(Enum(FitnessGoal), nullable=True)
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.BEGINNER)
    equipment_access = Column(Enum(EquipmentAccess), default=EquipmentAccess.BODYWEIGHT)
    training_frequency = Column(Integer, default=3)  # times per week

    # Dietary Preferences
    dietary_restrictions = Column(Text, nullable=True)  # JSON string
    allergies = Column(Text, nullable=True)  # JSON string

    # Goals
    target_weight = Column(Float, nullable=True)
    target_body_fat = Column(Float, nullable=True)
    goal_timeframe = Column(Integer, nullable=True)  # in weeks

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    onboarding_completed = Column(Boolean, default=False)

    # Relationships
    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")
    workout_sessions = relationship("WorkoutSession", back_populates="user", cascade="all, delete-orphan")
    nutrition_plans = relationship("NutritionPlan", back_populates="user", cascade="all, delete-orphan")
    meal_logs = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    progress_logs = relationship("ProgressLog", back_populates="user", cascade="all, delete-orphan")
    body_metrics = relationship("BodyMetrics", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
