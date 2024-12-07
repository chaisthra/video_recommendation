from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    # Base URL and Authentication
    BASE_URL: str = "https://api.socialverseapp.com"
    FLIC_TOKEN: str = "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8"
    RESONANCE_ALGORITHM: str = "resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if"
    
    # API Headers
    HEADERS: Dict[str, str] = {
        "Flic-Token": "flic_6e2d8d25dc29a4ddd382c2383a903cf4a688d1a117f6eb43b35a1e7fadbb84b8",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # API Endpoints
    ENDPOINTS: Dict[str, str] = {
        'viewed': '/posts/view',
        'liked': '/posts/like',
        'inspired': '/posts/inspire',
        'rated': '/posts/rating',
        'posts': '/posts/summary/get',
        'users': '/users/get_all'
    }
    
    # API Parameters
    DEFAULT_PAGE_SIZE: int = 1000
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAXSIZE: int = 1000

    class Config:
        env_file = ".env"

settings = Settings()