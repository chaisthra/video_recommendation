import asyncio
import httpx
import logging
from typing import Optional, Dict, List, Any
from ..core.config import settings
import json

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=settings.HEADERS
        )
        logger.info("DataFetcher initialized")

    async def fetch_data(self, endpoint: str, params: dict) -> List[Dict]:
        """Generic method to fetch data from any endpoint"""
        try:
            logger.info(f"Fetching data from {endpoint}")
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Parsed data structure: {json.dumps(data, indent=2)[:1000]}")
            
            # Handle different response formats
            if isinstance(data, dict):
                if not data:  # Empty dictionary
                    return []
                if 'posts' in data:
                    result = data['posts']
                elif 'data' in data:
                    result = data['data']
                else:
                    result = [data]
            elif isinstance(data, list):
                result = data
            else:
                result = [data] if data else []
            
            # Ensure result is a list of dictionaries
            if isinstance(result, list):
                result = [r for r in result if isinstance(r, dict)]
            else:
                result = []
                
            logger.info(f"Retrieved {len(result)} items from {endpoint}")
            return result
                
        except Exception as e:
            logger.error(f"Error fetching data from {endpoint}: {str(e)}")
            return []

    async def get_all_data(self) -> Dict[str, Any]:
        """Fetch all required data from endpoints"""
        try:
            # Define interaction endpoints
            interaction_params = {
                "page_size": settings.DEFAULT_PAGE_SIZE,
                "resonance_algorithm": settings.RESONANCE_ALGORITHM
            }
            
            tasks = []
            
            # Fetch interactions
            for endpoint in ['viewed', 'liked', 'inspired', 'rated']:
                url = f"{settings.BASE_URL}{settings.ENDPOINTS[endpoint]}"
                tasks.append(self.fetch_data(url, interaction_params))
            
            # Fetch posts and users
            tasks.extend([
                self.fetch_data(
                    f"{settings.BASE_URL}{settings.ENDPOINTS['posts']}", 
                    {"page_size": settings.DEFAULT_PAGE_SIZE}
                ),
                self.fetch_data(
                    f"{settings.BASE_URL}{settings.ENDPOINTS['users']}", 
                    {"page_size": settings.DEFAULT_PAGE_SIZE}
                )
            ])
            
            results = await asyncio.gather(*tasks)
            
            data = {
                'interactions': {
                    'viewed': results[0],
                    'liked': results[1],
                    'inspired': results[2],
                    'rated': results[3]
                },
                'posts': results[4],
                'users': results[5]
            }
            
            logger.info("\nData Summary:")
            logger.info(f"Posts: {len(data['posts'])}")
            logger.info(f"Users: {len(data['users'])}")
            for key, interactions in data['interactions'].items():
                logger.info(f"{key.capitalize()} interactions: {len(interactions)}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error in get_all_data: {str(e)}")
            return {
                'interactions': {
                    'viewed': [],
                    'liked': [],
                    'inspired': [],
                    'rated': []
                },
                'posts': [],
                'users': []
            }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()