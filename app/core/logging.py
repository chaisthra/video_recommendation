import logging
import sys
from typing import Any

# Configure logging format
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging() -> None:
    """Configure logging settings for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format=LOGGING_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

def get_logger(name: str) -> Any:
    """Get a logger instance with the specified name"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

# Custom logging function for recommendation events
def log_recommendation_event(
    username: str,
    recommendations: list,
    category_id: int = None,
    mood: str = None
) -> None:
    """Log recommendation events with relevant details"""
    logger = get_logger("recommendation_events")
    logger.info(
        f"Recommendations generated for user: {username} | "
        f"Category: {category_id} | Mood: {mood} | "
        f"Count: {len(recommendations)}"
    )

# Custom logging function for user interactions
def log_interaction_event(
    username: str,
    post_id: int,
    interaction_type: str,
    rating: float = None
) -> None:
    """Log user interaction events"""
    logger = get_logger("interaction_events")
    logger.info(
        f"User interaction recorded | User: {username} | "
        f"Post: {post_id} | Type: {interaction_type} | "
        f"Rating: {rating}"
    )