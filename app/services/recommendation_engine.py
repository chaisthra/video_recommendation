import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        logger.info("Initializing recommendation engine")
        self.user_profiles = self._build_user_profiles()
        self.post_lookup = {str(post['id']): post for post in self.data['posts']}
        logger.info(f"Built lookup for {len(self.post_lookup)} posts")

    def is_personalized(self, username: str) -> bool:
        """Check if recommendations are personalized for the user"""
        # Check if user has any interaction history
        for interaction_type in self.data['interactions'].values():
            for interaction in interaction_type:
                if interaction.get('username') == username:
                    return True
        return False

    def get_recommendation_quality(self, recommendations: List[Dict]) -> float:
        """Calculate recommendation quality score"""
        if not recommendations:
            return 0.0
            
        try:
            # Calculate average engagement score
            total_engagement = sum(
                float(rec.get('engagement_score', 0)) 
                for rec in recommendations
            )
            avg_engagement = total_engagement / len(recommendations)
            
            # Calculate diversity score (based on category distribution)
            categories = set(rec.get('category', {}).get('id') for rec in recommendations)
            diversity_score = len(categories) / len(recommendations)
            
            # Combine scores
            quality_score = (avg_engagement * 0.7) + (diversity_score * 0.3)
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Error calculating recommendation quality: {str(e)}")
            return 0.0

    def _build_user_profiles(self) -> Dict[str, Dict[str, float]]:
        """Build user profiles based on their interactions"""
        user_profiles = {}
        interaction_weights = {
            'viewed': 1.0,
            'liked': 3.0,
            'inspired': 4.0,
            'rated': 2.0
        }

        try:
            for interaction_type, interactions in self.data['interactions'].items():
                base_weight = interaction_weights.get(interaction_type, 1.0)
                
                for interaction in interactions:
                    user_id = str(interaction.get('id', ''))
                    post_id = str(interaction.get('post_id', ''))
                    
                    if not user_id or not post_id:
                        continue
                    
                    if user_id not in user_profiles:
                        user_profiles[user_id] = {}
                    
                    weight = base_weight
                    if interaction_type == 'rated':
                        rating = float(interaction.get('rating', 0)) / 100.0
                        weight *= (1 + rating)
                    
                    if post_id not in user_profiles[user_id]:
                        user_profiles[user_id][post_id] = 0
                    
                    user_profiles[user_id][post_id] += weight

            logger.info(f"Built profiles for {len(user_profiles)} users")
            return user_profiles
            
        except Exception as e:
            logger.error(f"Error building user profiles: {str(e)}")
            return {}

    def get_recommendations(
        self,
        username: str,
        category_id: Optional[int] = None,
        mood: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        try:
            available_posts = self.data['posts']
            if not available_posts:
                logger.warning("No posts available for recommendations")
                return []

            # Filter by category if specified
            if category_id is not None:
                available_posts = [
                    post for post in available_posts
                    if post.get('category', {}).get('id') == category_id
                ]
                logger.info(f"Filtered to {len(available_posts)} posts for category {category_id}")

            # Calculate scores
            post_scores = []
            for post in available_posts:
                score = self._calculate_post_score(post, mood)
                post_scores.append((post, score))

            # Sort by score and return top recommendations
            recommendations = sorted(post_scores, key=lambda x: x[1], reverse=True)
            result = [post for post, _ in recommendations[:limit]]
            
            logger.info(f"Generated {len(result)} recommendations")
            return result

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _calculate_post_score(self, post: Dict[str, Any], mood: Optional[str] = None) -> float:
        """Calculate overall score for a post"""
        try:
            base_score = (
                float(post.get('view_count', 0)) * 0.1 +
                float(post.get('upvote_count', 0)) * 1.5 +
                float(post.get('share_count', 0)) * 2.0 +
                float(post.get('average_rating', 0)) * 0.5
            )
            
            # Apply mood modifier if specified
            if mood:
                mood_score = self._calculate_mood_score(post, mood)
                base_score *= (1 + mood_score)
            
            # Apply recency boost
            created_at = post.get('created_at')
            if created_at:
                days_old = (datetime.now() - datetime.fromtimestamp(created_at / 1000.0)).days
                recency_boost = max(0, (30 - days_old)) / 30.0
                base_score *= (1 + recency_boost)
            
            return base_score
            
        except Exception as e:
            logger.error(f"Error calculating post score: {str(e)}")
            return 0.0

    def _calculate_mood_score(self, post: Dict[str, Any], mood: str) -> float:
        """Calculate mood compatibility score"""
        try:
            mood_mapping = {
                'happy': 1.0,
                'inspired': 0.8,
                'calm': 0.6,
                'focused': 0.4,
                'energetic': 0.2
            }
            
            mood_value = mood_mapping.get(mood.lower(), 0.5)
            post_summary = post.get('post_summary', {})
            
            # Check emotions in post summary
            post_emotions = post_summary.get('emotions', [])
            if isinstance(post_emotions, list):
                matching_emotions = sum(1 for emotion in post_emotions 
                                     if emotion.lower() == mood.lower())
                return matching_emotions / len(post_emotions) if post_emotions else 0.5
            
            return mood_value
            
        except Exception as e:
            logger.error(f"Error calculating mood score: {str(e)}")
            return 0.5