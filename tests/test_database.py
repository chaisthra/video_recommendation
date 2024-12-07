import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, User, UserInteraction, UserPreference
from datetime import datetime

def test_create_user(db_service):
    """Test user creation"""
    username = "test_user"
    db_service.record_interaction(
        username=username,
        post_id=1,
        interaction_type="view"
    )
    
    session = db_service.SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    
    assert user is not None
    assert user.username == username

def test_record_interaction(db_service):
    """Test recording user interactions"""
    username = "test_user"
    post_id = 1
    
    # First create user and interaction
    db_service.record_interaction(
        username=username,
        post_id=post_id,
        interaction_type="view"
    )
    
    session = db_service.SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    interactions = session.query(UserInteraction).filter_by(user_id=user.id).all()
    session.close()
    
    assert len(interactions) == 1
    assert interactions[0].interaction_type == "view"
    assert interactions[0].post_id == post_id

def test_record_rating(db_service):
    """Test recording ratings"""
    username = "test_user"
    post_id = 1
    rating = 4.5
    
    db_service.record_interaction(
        username=username,
        post_id=post_id,
        interaction_type="rate",
        rating=rating
    )
    
    session = db_service.SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    interaction = session.query(UserInteraction)\
        .filter_by(user_id=user.id, post_id=post_id)\
        .first()
    session.close()
    
    assert interaction is not None
    assert interaction.rating == rating

def test_get_user_history(db_service):
    """Test retrieving user history"""
    username = "test_user"
    post_id = 1
    
    # Create a view interaction
    db_service.record_interaction(
        username=username,
        post_id=post_id,
        interaction_type="view"
    )
    
    history = db_service.get_user_history(username)
    
    assert isinstance(history, dict)
    assert "views" in history
    assert "likes" in history
    assert "ratings" in history
    assert len(history["views"]) == 1
    assert history["views"][0]["post_id"] == post_id

def test_handle_duplicate_interactions(db_service):
    """Test handling duplicate interactions"""
    username = "test_user"
    post_id = 1
    
    # Record same interaction twice
    db_service.record_interaction(
        username=username,
        post_id=post_id,
        interaction_type="view"
    )
    db_service.record_interaction(
        username=username,
        post_id=post_id,
        interaction_type="view"
    )
    
    session = db_service.SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    interactions = session.query(UserInteraction)\
        .filter_by(user_id=user.id, post_id=post_id)\
        .all()
    session.close()
    
    assert len(interactions) == 2

def test_update_preferences(db_service):
    """Test updating user preferences"""
    username = "test_user"
    
    # Create a like interaction to trigger preference update
    db_service.record_interaction(
        username=username,
        post_id=1,
        interaction_type="like"
    )
    
    session = db_service.SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    preferences = session.query(UserPreference)\
        .filter_by(user_id=user.id)\
        .all()
    session.close()
    
    assert len(preferences) > 0
    assert all(p.preference_score > 0 for p in preferences)

def test_handle_invalid_interaction_type(db_service):
    """Test handling invalid interaction types"""
    with pytest.raises(ValueError):
        db_service.record_interaction(
            username="test_user",
            post_id=1,
            interaction_type="invalid_type"
        )

def test_handle_invalid_rating(db_service):
    """Test handling invalid rating values"""
    with pytest.raises(ValueError):
        db_service.record_interaction(
            username="test_user",
            post_id=1,
            interaction_type="rate",
            rating=6.0  # Invalid rating > 5.0
        )

def test_cleanup(db_service):
    """Test database cleanup"""
    session = db_service.SessionLocal()
    
    # Use text() for raw SQL
    result = session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    ).fetchall()
    
    session.close()
    assert len(result) > 0