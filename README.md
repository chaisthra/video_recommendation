# Video Recommendation System

A sophisticated recommendation system that suggests videos based on user preferences and engagement patterns, leveraging user interaction data and video metadata.

## 🎯 Features

- Personalized video recommendations based on user history
- Content-based and collaborative filtering
- Mood-based recommendations
- Category filtering
- Cold start problem handling
- Caching system for improved performance
- RESTful API endpoints

## 🛠️ Technology Stack

- Python 3.8+
- FastAPI
- scikit-learn
- pandas
- numpy
- httpx
- cachetools

## 📊 Project Structure

```
video_recommendation/
│
├── app/
│   ├── core/            # Core configuration
│   ├── database/        # Database models and service
│   ├── services/        # Business logic
│   └── api/            # API endpoints
│
├── tests/              # Test suite
└── data/              # Data storage
```

## 🚀 Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd video_recommendation
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.main:app --reload --port 8000
```

## 📝 API Endpoints

### GET /feed
Get personalized video recommendations

Parameters:
- `username` (required): User's username
- `category_id` (optional): Filter by category ID
- `mood` (optional): Filter by mood (happy, sad, excited, calm, anxious)

Example requests:
```bash
# Basic request
curl "http://localhost:8000/feed?username=user123"

# With category
curl "http://localhost:8000/feed?username=user123&category_id=1"

# With mood
curl "http://localhost:8000/feed?username=user123&mood=happy"

# With both category and mood
curl "http://localhost:8000/feed?username=user123&category_id=1&mood=happy"
```
### Interaction Endpoints

1. **Record User Interaction**:
```bash
POST /interactions
{
    "username": "string",
    "post_id": integer,
    "interaction_type": "view" | "like" | "rate",
    "rating": float (optional)
}
```

2. **Get User History**:
```bash
GET /interactions/{username}
```

## 🔍 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific tests
pytest tests/test_api.py
```

## 🧮 Algorithm Details

The recommendation system uses a hybrid approach combining:

1. Content-based filtering:
   - Video categories
   - Mood matching
   - Engagement scores

2. Collaborative filtering:
   - User interaction history
   - Weighted scoring system:
     - Views: 1x
     - Likes: 2x
     - Inspires: 3x
     - Ratings: 4x

3. Cold Start Handling:
   - Engagement-based recommendations
   - Category matching
   - Mood-based filtering

## 🔐 Security

- Authentication using Flic-Token
- Secure data handling
- Rate limiting implementation

## 📊 Performance

- Async API calls
- Efficient data caching
- Optimized database queries
- Response time monitoring

## 🎯 Future Improvements

1. Real-time recommendations
2. A/B testing framework
3. Advanced personalization
4. Performance optimization
5. Enhanced metrics


## License

[MIT License](LICENSE)