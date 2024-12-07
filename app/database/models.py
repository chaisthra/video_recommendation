from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interactions = relationship("UserInteraction", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, nullable=False)
    interaction_type = Column(String, nullable=False)  # 'view', 'like', 'rate'
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="interactions")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, nullable=False)
    preference_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="preferences")

# Database initialization
DATABASE_URL = "sqlite:///./recommendation_system.db"
engine = create_engine(DATABASE_URL)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)