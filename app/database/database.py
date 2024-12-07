from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from datetime import datetime
from typing import List, Dict, Any
import logging
from pathlib import Path
from ..database.models import Base, User, UserInteraction, UserPreference

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.database_path = data_dir / "recommendation_system.db"
        self.database_url = f"sqlite:///{self.database_path}"
        logger.info(f"Initializing database at {self.database_url}")
        
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("Database initialized successfully")

    def validate_interaction(self, interaction_type: str, rating: float = None):
        """Validate interaction data"""
        valid_types = ["view", "like", "rate", "inspire"]
        if interaction_type not in valid_types:
            raise ValueError(f"Invalid interaction type. Must be one of: {valid_types}")
            
        if interaction_type == "rate":
            if rating is None:
                raise ValueError("Rating is required for rate interactions")
            if not 0 <= rating <= 5:
                raise ValueError("Rating must be between 0 and 5")

    def record_interaction(self, username: str, post_id: int, interaction_type: str, rating: float = None):
        """Record a user's interaction with a post"""
        session = self.SessionLocal()
        try:
            # Validate input before starting database transaction
            self.validate_interaction(interaction_type, rating)
            
            # Get or create user
            user = session.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username)
                session.add(user)
                session.flush()

            # Create interaction
            interaction = UserInteraction(
                user_id=user.id,
                post_id=post_id,
                interaction_type=interaction_type,
                rating=rating,
                created_at=datetime.utcnow()
            )
            session.add(interaction)
            
            # Update preferences
            if interaction_type in ["like", "rate"] and (rating is None or rating > 3):
                self._update_user_preferences(session, user.id, post_id)

            session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error recording interaction: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    def _update_user_preferences(self, session, user_id: int, post_id: int):
        """Update user's category preferences"""
        try:
            pref = session.query(UserPreference)\
                .filter_by(user_id=user_id, category_id=1)\
                .first()
            
            if pref:
                pref.preference_score += 1
                pref.last_updated = datetime.utcnow()
            else:
                pref = UserPreference(
                    user_id=user_id,
                    category_id=1,
                    preference_score=1
                )
                session.add(pref)
                
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            raise

    def get_user_history(self, username: str) -> Dict[str, List[Dict]]:
        """Get user's interaction history"""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return {
                    'views': [],
                    'likes': [],
                    'ratings': []
                }

            interactions = session.query(UserInteraction)\
                .filter_by(user_id=user.id)\
                .order_by(UserInteraction.created_at.desc())\
                .all()

            history = {
                'views': [],
                'likes': [],
                'ratings': []
            }

            for interaction in interactions:
                interaction_data = {
                    'post_id': interaction.post_id,
                    'timestamp': interaction.created_at.isoformat()
                }
                if interaction.rating:
                    interaction_data['rating'] = interaction.rating
                
                if interaction.interaction_type == 'view':
                    history['views'].append(interaction_data)
                elif interaction.interaction_type == 'like':
                    history['likes'].append(interaction_data)
                elif interaction.interaction_type == 'rate':
                    history['ratings'].append(interaction_data)

            return history

        except Exception as e:
            logger.error(f"Error fetching user history: {str(e)}")
            raise
        finally:
            session.close()

    def get_user_preferences(self, username: str) -> Dict[int, float]:
        """Get user's category preferences"""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return {}

            preferences = session.query(UserPreference)\
                .filter_by(user_id=user.id)\
                .all()

            return {
                pref.category_id: pref.preference_score 
                for pref in preferences
            }

        except Exception as e:
            logger.error(f"Error fetching user preferences: {str(e)}")
            raise
        finally:
            session.close()