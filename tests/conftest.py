import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.database.database import DatabaseService
import os

@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_service(test_db):
    """Create database service with test database"""
    service = DatabaseService()
    service.engine = test_db.get_bind()
    service.SessionLocal = sessionmaker(bind=service.engine)
    return service

@pytest.fixture
def sample_data():
    """Create sample data for testing"""
    return {
        'posts': [
            {
                'id': 1,
                'category': {'id': 2, 'name': 'Vible'},
                'title': 'Test Post 1',
                'view_count': 100,
                'upvote_count': 50,
                'rating_count': 10,
                'average_rating': 4.5,
                'share_count': 5,
                'created_at': 1698088807000,
                'post_summary': {
                    'emotions': ['happy', 'inspired']
                }
            },
            {
                'id': 2,
                'category': {'id': 2, 'name': 'Vible'},
                'title': 'Test Post 2',
                'view_count': 200,
                'upvote_count': 75,
                'rating_count': 15,
                'average_rating': 4.0,
                'share_count': 8,
                'created_at': 1698088807000,
                'post_summary': {
                    'emotions': ['calm', 'focused']
                }
            }
        ],
        'interactions': {
            'viewed': [
                {'user_id': 1, 'post_id': 1, 'username': 'test_user'},
                {'user_id': 1, 'post_id': 2, 'username': 'test_user'}
            ],
            'liked': [
                {'user_id': 1, 'post_id': 1, 'username': 'test_user'}
            ],
            'rated': [
                {'user_id': 1, 'post_id': 1, 'username': 'test_user', 'rating': 4.5}
            ],
            'inspired': [
                {'user_id': 1, 'post_id': 1, 'username': 'test_user'}
            ]
        },
        'users': [
            {'id': 1, 'username': 'test_user'}
        ]
    }

@pytest.fixture
def mock_response(sample_data):
    """Create mock API response"""
    return {
        "status": "success",
        "data": sample_data['posts']
    }

@pytest.fixture
def app_client():
    """Create test client for FastAPI app"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_database(test_db):
    """Set up test database before each test"""
    Base.metadata.create_all(bind=test_db.get_bind())
    yield
    Base.metadata.drop_all(bind=test_db.get_bind())