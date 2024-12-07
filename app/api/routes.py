import logging
import time
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from cachetools import TTLCache
from ..core.config import settings
from ..services.data_fetcher import DataFetcher
from ..services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

router = APIRouter()
posts_cache = TTLCache(maxsize=settings.CACHE_MAXSIZE, ttl=settings.CACHE_TTL)

class PostResponse(BaseModel):
    id: int
    title: str
    category_id: Optional[int] = None
    view_count: Optional[int] = None
    upvote_count: Optional[int] = None
    rating_count: Optional[int] = None
    average_rating: Optional[float] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    total_count: int
    has_more: bool = False
    is_personalized: bool = False
    performance_metrics: Dict[str, float]

@router.get("/feed", response_model=RecommendationResponse)
async def get_feed(
    username: str = Query(..., description="Username to get recommendations for"),
    category_id: Optional[int] = Query(None, description="Category ID to filter recommendations"),
    mood: Optional[str] = Query(None, description="User's current mood (happy, sad, excited, calm, anxious)"),
    limit: int = Query(10, description="Number of recommendations to return", ge=1, le=50)
):
    """Get personalized video recommendations"""
    try:
        cache_key = f"{username}:{category_id}:{mood}:{limit}"
        if cache_key in posts_cache:
            return JSONResponse(content=posts_cache[cache_key])
        
        start_time = time.time()
        data_fetcher = DataFetcher()
        
        try:
            data = await data_fetcher.get_all_data()
            engine = RecommendationEngine(data)
            
            recommendations = engine.get_recommendations(
                username=username,
                category_id=category_id,
                mood=mood,
                limit=limit
            )
            
            processing_time = time.time() - start_time
            
            response = {
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "has_more": len(recommendations) == limit,
                "is_personalized": engine.is_personalized(username),
                "performance_metrics": {
                    "processing_time_seconds": processing_time
                }
            }
            
            posts_cache[cache_key] = response
            return JSONResponse(content=response)
            
        finally:
            await data_fetcher.close()
            
    except Exception as e:
        logger.error(f"Error processing recommendation request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))