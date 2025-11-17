"""
Progress tracking models.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class BodyMetrics(Base):
    """User's body measurements over time."""

    __tablename__ = "body_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Measurements
    weight = Column(Float, nullable=False)  # kg
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)  # kg
    bmi = Column(Float, nullable=True)

    # Body Measurements (in cm)
    chest = Column(Float, nullable=True)
    waist = Column(Float, nullable=True)
    hips = Column(Float, nullable=True)
    bicep_left = Column(Float, nullable=True)
    bicep_right = Column(Float, nullable=True)
    thigh_left = Column(Float, nullable=True)
    thigh_right = Column(Float, nullable=True)
    calf_left = Column(Float, nullable=True)
    calf_right = Column(Float, nullable=True)

    notes = Column(Text)

    # Timestamps
    measured_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="body_metrics")

    def __repr__(self):
        return f"<BodyMetrics(id={self.id}, user_id={self.user_id}, weight={self.weight}, measured_at={self.measured_at})>"


class ProgressLog(Base):
    """General progress logs and notes."""

    __tablename__ = "progress_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    log_type = Column(String(50), default="general")  # general, achievement, issue, note

    # AI Analysis
    ai_feedback = Column(Text, nullable=True)  # AI-generated insights
    sentiment_score = Column(Float, nullable=True)  # -1 to 1

    # Timestamps
    log_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="progress_logs")

    def __repr__(self):
        return f"<ProgressLog(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
