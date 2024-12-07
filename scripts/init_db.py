from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with required tables"""
    try:
        # Create database engine
        SQLALCHEMY_DATABASE_URL = "sqlite:///./data/recommendation_system.db"
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test database connection
        with SessionLocal() as session:
            session.execute("SELECT 1")
            logger.info("Database connection test successful")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()