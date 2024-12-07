from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..database.database import DatabaseService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
db_service = DatabaseService()

class InteractionCreate(BaseModel):
    username: str
    post_id: int
    interaction_type: str
    rating: Optional[float] = None

@router.post("")
async def record_interaction(interaction: InteractionCreate):
    """Record a user interaction with a post"""
    try:
        db_service.record_interaction(
            username=interaction.username,
            post_id=interaction.post_id,
            interaction_type=interaction.interaction_type,
            rating=interaction.rating
        )
        return {"status": "success"}
    except ValueError as ve:
        # Handle validation errors
        logger.warning(f"Validation error: {str(ve)}")
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        # Handle other errors
        logger.error(f"Error recording interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{username}")
async def get_user_interactions(username: str):
    """Get a user's interaction history"""
    try:
        history = db_service.get_user_history(username)
        return {
            "username": username,
            "history": history,
            "preferences": db_service.get_user_preferences(username)
        }
    except Exception as e:
        logger.error(f"Error fetching interactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))