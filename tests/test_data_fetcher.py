import pytest
import httpx
from unittest.mock import Mock, patch
from app.services.data_fetcher import DataFetcher
from app.core.config import settings

class MockResponse:
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code
        self.text = str(data)

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPError(f"HTTP Error: {self.status_code}")

@pytest.mark.asyncio
async def test_fetch_posts_data():
    """Test fetching posts data"""
    mock_data = {"posts": [{"id": 1}, {"id": 2}]}
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = MockResponse(mock_data)
        
        data_fetcher = DataFetcher()
        params = {"page_size": 1000}
        data = await data_fetcher.fetch_data("/test/endpoint", params)
        
        assert isinstance(data, list)
        assert len(data) == 2
        assert all(isinstance(item, dict) for item in data)

@pytest.mark.asyncio
async def test_get_all_data():
    """Test getting all data types"""
    mock_data = {"data": [{"id": 1}]}
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = MockResponse(mock_data)
        
        data_fetcher = DataFetcher()
        data = await data_fetcher.get_all_data()
        
        assert isinstance(data, dict)
        assert 'posts' in data
        assert 'users' in data
        assert 'interactions' in data
        assert isinstance(data['interactions'], dict)

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling when fetching data"""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        data_fetcher = DataFetcher()
        params = {"page_size": 1000}
        data = await data_fetcher.fetch_data("/test/endpoint", params)
        
        assert isinstance(data, list)
        assert len(data) == 0

@pytest.mark.asyncio
async def test_pagination_handling():
    """Test handling of paginated responses"""
    mock_responses = [
        MockResponse({"data": [{"id": 1}, {"id": 2}]}),
        MockResponse({"data": []})
    ]
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = mock_responses
        
        data_fetcher = DataFetcher()
        params = {"page_size": 1000}
        data = await data_fetcher.fetch_data("/test/endpoint", params)
        
        assert isinstance(data, list)
        assert len(data) == 2

@pytest.mark.asyncio
async def test_client_cleanup():
    """Test proper cleanup of HTTP client"""
    data_fetcher = DataFetcher()
    await data_fetcher.close()

@pytest.mark.asyncio
async def test_response_processing():
    """Test processing of different response formats"""
    # Test list response
    mock_data = [{"id": 1}, {"id": 2}]
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = MockResponse(mock_data)
        
        data_fetcher = DataFetcher()
        params = {"page_size": 1000}
        data = await data_fetcher.fetch_data("/test/endpoint", params)
        assert len(data) == 2
        
        # Test dict response with data key
        mock_get.return_value = MockResponse({"data": [{"id": 1}]})
        data = await data_fetcher.fetch_data("/test/endpoint", params)
        assert len(data) == 1
        
        # Test dict response with posts key
        mock_get.return_value = MockResponse({"posts": [{"id": 1}, {"id": 2}]})
        data = await data_fetcher.fetch_data("/test/endpoint", params)
        assert len(data) == 2

@pytest.mark.asyncio
async def test_response_formats():
    """Test handling of various response formats"""
    test_cases = [
        ({"posts": [{"id": 1}]}, 1),
        ({"data": [{"id": 1}, {"id": 2}]}, 2),
        ([{"id": 1}, {"id": 2}, {"id": 3}], 3),
        ({"id": 1}, 1),
        ({}, 0),
        ([], 0)
    ]
    
    data_fetcher = DataFetcher()
    params = {"page_size": 1000}
    
    for response_data, expected_length in test_cases:
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = MockResponse(response_data)
            data = await data_fetcher.fetch_data("/test/endpoint", params)
            assert len(data) == expected_length

@pytest.mark.asyncio
async def test_error_response_codes():
    """Test handling of different HTTP error codes"""
    error_codes = [400, 401, 403, 404, 500, 502, 503]
    
    data_fetcher = DataFetcher()
    params = {"page_size": 1000}
    
    for code in error_codes:
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value = MockResponse({"error": "Test error"}, status_code=code)
            data = await data_fetcher.fetch_data("/test/endpoint", params)
            assert isinstance(data, list)
            assert len(data) == 0