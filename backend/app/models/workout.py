"""
Workout and exercise models.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class MuscleGroup(str, enum.Enum):
    """Muscle group types."""
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    LEGS = "legs"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    ABS = "abs"
    CORE = "core"
    FULL_BODY = "full_body"


class ExerciseType(str, enum.Enum):
    """Exercise types."""
    COMPOUND = "compound"
    ISOLATION = "isolation"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"


class WorkoutType(str, enum.Enum):
    """Workout split types."""
    PUSH_PULL_LEGS = "push_pull_legs"
    UPPER_LOWER = "upper_lower"
    BODY_PART_SPLIT = "body_part_split"
    FULL_BODY = "full_body"
    CUSTOM = "custom"


class Exercise(Base):
    """Exercise library."""

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    muscle_group = Column(Enum(MuscleGroup), nullable=False)
    exercise_type = Column(Enum(ExerciseType), default=ExerciseType.COMPOUND)
    equipment_required = Column(String(255))
    difficulty_level = Column(Integer, default=1)  # 1-5
    video_url = Column(String(500), nullable=True)
    instructions = Column(Text)

    # Relationships
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")

    def __repr__(self):
        return f"<Exercise(id={self.id}, name='{self.name}', muscle_group='{self.muscle_group}')>"


class WorkoutPlan(Base):
    """User's workout plan."""

    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    workout_type = Column(Enum(WorkoutType), default=WorkoutType.CUSTOM)
    frequency_per_week = Column(Integer, default=3)
    duration_weeks = Column(Integer, default=12)
    is_active = Column(Boolean, default=True)

    # AI Generated Context
    generation_prompt = Column(Text)  # Store the prompt used to generate this plan
    ai_rationale = Column(Text)  # Why the AI chose this plan

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="workout_plans")
    workout_sessions = relationship("WorkoutSession", back_populates="workout_plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkoutPlan(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class WorkoutSession(Base):
    """Individual workout session."""

    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=True)
    name = Column(String(255), nullable=False)
    day_of_week = Column(Integer, nullable=True)  # 0-6 (Monday-Sunday)
    target_muscle_groups = Column(Text)  # JSON string of muscle groups
    notes = Column(Text)
    completed = Column(Boolean, default=False)

    # Timestamps
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="workout_sessions")
    workout_plan = relationship("WorkoutPlan", back_populates="workout_sessions")
    exercises = relationship("WorkoutExercise", back_populates="workout_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkoutSession(id={self.id}, name='{self.name}', completed={self.completed})>"


class WorkoutExercise(Base):
    """Exercise within a workout session."""

    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, default=0)

    # Prescription
    sets = Column(Integer, default=3)
    reps = Column(Integer, default=10)
    rest_seconds = Column(Integer, default=60)
    weight = Column(Float, nullable=True)  # in kg
    duration_seconds = Column(Integer, nullable=True)  # for cardio/timed exercises

    # Actual Performance
    actual_sets = Column(Integer, nullable=True)
    actual_reps = Column(Integer, nullable=True)
    actual_weight = Column(Float, nullable=True)
    actual_duration_seconds = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False)

    notes = Column(Text)

    # Relationships
    workout_session = relationship("WorkoutSession", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")

    def __repr__(self):
        return f"<WorkoutExercise(id={self.id}, exercise_id={self.exercise_id}, sets={self.sets}, reps={self.reps})>"
