import pytest
from app.services.recommendation_engine import RecommendationEngine
from datetime import datetime, timedelta

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {
        'interactions': {
            'viewed': [
                {'user_id': 1, 'post_id': 1},
                {'user_id': 1, 'post_id': 2}
            ],
            'liked': [
                {'user_id': 1, 'post_id': 1}
            ],
            'inspired': [
                {'user_id': 1, 'post_id': 1}
            ],
            'rated': [
                {'user_id': 1, 'post_id': 1, 'rating': 5}
            ]
        },
        'posts': [
            {
                'id': 1,
                'category_id': 1,
                'mood_score': 1,
                'engagement_score': 0.8,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'category_id': 1,
                'mood_score': 2,
                'engagement_score': 0.9,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 3,
                'category_id': 2,
                'mood_score': 1,
                'engagement_score': 0.7,
                'created_at': datetime.now().isoformat()
            }
        ],
        'users': [
            {'id': 1, 'username': 'test_user'},
            {'id': 2, 'username': 'new_user'}
        ]
    }

@pytest.fixture
def engine(sample_data):
    """Create a RecommendationEngine instance with sample data."""
    return RecommendationEngine(sample_data)

def test_user_profile_building(engine):
    """Test if user profiles are built correctly."""
    profiles = engine.user_profiles
    assert 1 in profiles
    assert len(profiles[1]) == 2  # User 1 has interacted with 2 posts

def test_content_features_building(engine):
    """Test if content features are built correctly."""
    features = engine.content_features
    assert len(features) == 3  # Should have features for all 3 posts
    assert all(key in features[1] for key in ['category_id', 'mood_score', 'engagement_score', 'creation_time'])

def test_recommendations_for_existing_user(engine):
    """Test recommendations for an existing user."""
    recommendations = engine.get_recommendations('test_user', limit=2)
    assert len(recommendations) <= 2
    assert all(isinstance(rec, dict) for rec in recommendations)

def test_recommendations_with_category_filter(engine):
    """Test recommendations with category filtering."""
    recommendations = engine.get_recommendations('test_user', category_id=1)
    assert all(rec['category_id'] == 1 for rec in recommendations)

def test_recommendations_with_mood(engine):
    """Test recommendations with mood filtering."""
    recommendations = engine.get_recommendations('test_user', mood='happy')
    assert len(recommendations) > 0

def test_cold_start_recommendations(engine):
    """Test recommendations for new users."""
    recommendations = engine.get_recommendations('new_user')
    assert len(recommendations) > 0
    # Cold start should prioritize high engagement posts
    assert recommendations[0]['engagement_score'] >= recommendations[-1]['engagement_score']

def test_recommendations_with_invalid_user(engine):
    """Test recommendations for invalid users."""
    recommendations = engine.get_recommendations('invalid_user')
    assert len(recommendations) > 0  # Should return cold start recommendations