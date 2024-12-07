import pytest
from datetime import datetime
from typing import Dict, Any

def get_mock_posts() -> list:
    return [
        {
            "id": 1,
            "title": "Test Post 1",
            "category": {
                "id": 2,
                "name": "Vible",
                "count": 532
            },
            "view_count": 100,
            "upvote_count": 50,
            "rating_count": 10,
            "average_rating": 4.5,
            "created_at": int(datetime.now().timestamp() * 1000),
            "engagement_score": 0.8
        },
        {
            "id": 2,
            "title": "Test Post 2",
            "category": {
                "id": 2,
                "name": "Vible",
                "count": 532
            },
            "view_count": 200,
            "upvote_count": 75,
            "rating_count": 15,
            "average_rating": 4.0,
            "created_at": int(datetime.now().timestamp() * 1000),
            "engagement_score": 0.9
        }
    ]

def get_mock_users() -> list:
    return [
        {
            "id": 1,
            "username": "test_user"
        },
        {
            "id": 2,
            "username": "concurrent_test_user"
        }
    ]

def get_mock_interactions() -> Dict[str, list]:
    return {
        'viewed': [
            {
                'user_id': 1,
                'post_id': 1,
                'username': 'test_user'
            }
        ],
        'liked': [
            {
                'user_id': 1,
                'post_id': 1,
                'username': 'test_user'
            }
        ],
        'rated': [
            {
                'user_id': 1,
                'post_id': 1,
                'username': 'test_user',
                'rating': 4.5
            }
        ],
        'inspired': [
            {
                'user_id': 1,
                'post_id': 1,
                'username': 'test_user'
            }
        ]
    }

def get_mock_data() -> Dict[str, Any]:
    return {
        'posts': get_mock_posts(),
        'users': get_mock_users(),
        'interactions': get_mock_interactions()
    }