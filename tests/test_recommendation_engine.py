import pytest
from app.services.recommendation_engine import RecommendationEngine

def test_recommendation_engine_initialization(sample_data):
    """Test initialization of recommendation engine"""
    engine = RecommendationEngine(sample_data)
    assert engine.data == sample_data
    assert hasattr(engine, 'user_profiles')
    assert hasattr(engine, 'post_lookup')

def test_is_personalized(sample_data):
    """Test personalization check"""
    engine = RecommendationEngine(sample_data)
    assert engine.is_personalized('test_user') is True
    assert engine.is_personalized('new_user') is False

def test_get_recommendation_quality(sample_data):
    """Test recommendation quality calculation"""
    engine = RecommendationEngine(sample_data)
    recommendations = sample_data['posts']
    quality = engine.get_recommendation_quality(recommendations)
    assert 0 <= quality <= 1

def test_get_recommendations_with_category(sample_data):
    """Test getting recommendations with category filter"""
    engine = RecommendationEngine(sample_data)
    recommendations = engine.get_recommendations(
        username='test_user',
        category_id=2,
        limit=5
    )
    assert isinstance(recommendations, list)
    assert all(r['category']['id'] == 2 for r in recommendations)

def test_get_recommendations_with_mood(sample_data):
    """Test getting recommendations with mood filter"""
    engine = RecommendationEngine(sample_data)
    recommendations = engine.get_recommendations(
        username='test_user',
        mood='happy',
        limit=5
    )
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5

def test_cold_start_recommendations(sample_data):
    """Test recommendations for new users"""
    engine = RecommendationEngine(sample_data)
    recommendations = engine.get_recommendations(
        username='new_user',
        limit=5
    )
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5

def test_calculate_post_score(sample_data):
    """Test post scoring logic"""
    engine = RecommendationEngine(sample_data)
    post = sample_data['posts'][0]
    
    # Test basic scoring
    basic_score = engine._calculate_post_score(post)
    assert basic_score > 0
    
    # Test scoring with mood
    mood_score = engine._calculate_post_score(post, mood='happy')
    assert mood_score >= basic_score

def test_calculate_mood_score(sample_data):
    """Test mood scoring logic"""
    engine = RecommendationEngine(sample_data)
    post = sample_data['posts'][0]
    
    # Test with matching mood
    happy_score = engine._calculate_mood_score(post, 'happy')
    assert happy_score > 0
    
    # Test with non-matching mood
    sad_score = engine._calculate_mood_score(post, 'sad')
    assert sad_score >= 0

def test_recommendation_limit(sample_data):
    """Test recommendation limit enforcement"""
    engine = RecommendationEngine(sample_data)
    limit = 1
    recommendations = engine.get_recommendations(
        username='test_user',
        limit=limit
    )
    assert len(recommendations) <= limit

def test_error_handling(sample_data):
    """Test error handling in recommendations"""
    engine = RecommendationEngine(sample_data)
    
    # Test with invalid category
    recommendations = engine.get_recommendations(
        username='test_user',
        category_id=999,
        limit=5
    )
    assert isinstance(recommendations, list)
    assert len(recommendations) == 0

def test_recommendation_sorting(sample_data):
    """Test recommendation sorting"""
    engine = RecommendationEngine(sample_data)
    recommendations = engine.get_recommendations(
        username='test_user',
        limit=5
    )
    if len(recommendations) >= 2:
        first_score = engine._calculate_post_score(recommendations[0])
        second_score = engine._calculate_post_score(recommendations[1])
        assert first_score >= second_score