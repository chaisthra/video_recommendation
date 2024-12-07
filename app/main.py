from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .api.routes import router as recommendation_router
from .api.interaction_routes import router as interaction_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events
    """
    # Startup
    logger.info("Starting up the application")
    yield
    # Shutdown
    logger.info("Shutting down the application")

app = FastAPI(
    title="Video Recommendation API",
    description="API for personalized video recommendations",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=JSONResponse
)

# Include routers
app.include_router(recommendation_router, tags=["recommendations"])
app.include_router(interaction_router, prefix="/interactions", tags=["interactions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        workers=4
    )