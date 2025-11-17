"""
Nutrition and meal tracking models.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class MealType(str, enum.Enum):
    """Meal types."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"


class NutritionPlan(Base):
    """User's nutrition plan."""

    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Daily Targets
    daily_calories = Column(Float, nullable=False)
    daily_protein_g = Column(Float, nullable=False)
    daily_carbs_g = Column(Float, nullable=False)
    daily_fats_g = Column(Float, nullable=False)
    daily_fiber_g = Column(Float, nullable=True)

    # Meal Distribution
    meals_per_day = Column(Integer, default=3)

    # AI Context
    generation_rationale = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="nutrition_plans")

    def __repr__(self):
        return f"<NutritionPlan(id={self.id}, user_id={self.user_id}, daily_calories={self.daily_calories})>"


class FoodItem(Base):
    """Food items database."""

    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255), nullable=True)

    # Nutritional info per 100g
    calories_per_100g = Column(Float, nullable=False)
    protein_per_100g = Column(Float, nullable=False)
    carbs_per_100g = Column(Float, nullable=False)
    fats_per_100g = Column(Float, nullable=False)
    fiber_per_100g = Column(Float, nullable=True)

    # Common serving size
    serving_size_g = Column(Float, default=100)
    serving_description = Column(String(255))

    # Relationships
    meal_logs = relationship("MealLog", back_populates="food_item")

    def __repr__(self):
        return f"<FoodItem(id={self.id}, name='{self.name}')>"


class MealLog(Base):
    """User's meal logging."""

    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)

    # Meal Info
    meal_type = Column(Enum(MealType), nullable=False)
    meal_date = Column(DateTime(timezone=True), nullable=False)

    # Custom Entry (if food_item_id is None)
    custom_food_name = Column(String(255), nullable=True)
    serving_size_g = Column(Float, nullable=False)

    # Calculated Nutrition
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fats_g = Column(Float, nullable=False)
    fiber_g = Column(Float, nullable=True)

    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="meal_logs")
    food_item = relationship("FoodItem", back_populates="meal_logs")

    def __repr__(self):
        food_name = self.custom_food_name if self.custom_food_name else "food_item"
        return f"<MealLog(id={self.id}, user_id={self.user_id}, meal_type='{self.meal_type}', food='{food_name}')>"
