import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import httpx
import asyncio
import logging
from .test_fixtures import get_mock_data

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_data():
    return get_mock_data()

@pytest.fixture
def test_client():
    with patch('app.services.data_fetcher.DataFetcher.get_all_data') as mock_get_data:
        mock_get_data.return_value = get_mock_data()
        client = TestClient(app)
        yield client

def test_get_recommendations(test_client):
    """Test getting recommendations endpoint"""
    response = test_client.get("/feed?username=test_user")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "total_count" in data
    assert "is_personalized" in data
    assert "performance_metrics" in data

def test_invalid_interactions(test_client):
    """Test handling of invalid interactions"""
    # Invalid interaction type
    invalid_interaction = {
        "username": "test_user",
        "post_id": 1,
        "interaction_type": "invalid_type"
    }
    response = test_client.post("/interactions", json=invalid_interaction)
    assert response.status_code == 200
    assert response.json()["status"] == "error"

@pytest.mark.asyncio
async def test_concurrent_requests(test_client):
    """Test handling of concurrent requests"""
    # Create test data first
    interaction = {
        "username": "concurrent_test_user",
        "post_id": 1,
        "interaction_type": "view"
    }
    test_client.post("/interactions", json=interaction)
    
    async def make_concurrent_requests():
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            tasks = []
            for _ in range(3):
                tasks.append(
                    client.get("/feed", params={"username": "concurrent_test_user"})
                )
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return [r.status_code for r in responses if not isinstance(r, Exception)]
    
    response_codes = await make_concurrent_requests()
    assert len(response_codes) > 0
    assert all(code == 200 for code in response_codes)

def test_personalization_consistency(test_client):
    """Test consistency of personalization flag"""
    # Test new user (should not be personalized)
    response = test_client.get("/feed?username=new_test_user")
    assert response.status_code == 200
    data = response.json()
    assert not data["is_personalized"]
    
    # Test user with interactions
    response = test_client.get("/feed?username=test_user")
    assert response.status_code == 200
    data = response.json()
    assert data["is_personalized"]

def test_api_documentation(test_client):
    """Test API documentation endpoints"""
    response = test_client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema