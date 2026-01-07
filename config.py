import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    VISUAL_CROSSING_API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")
    VISUAL_CROSSING_BASE_URL = os.getenv(
        "VISUAL_CROSSING_BASE_URL",
        "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline",
    )
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))
    REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0")