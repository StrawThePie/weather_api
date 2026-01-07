import time
from typing import Dict, Any, Optional

import json
import requests
import redis

from config import Config

redis_client = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)


def _make_cache_key(
    city: str,
    state: Optional[str] = None,
    country: str = "US",
    unit_group: str = "metric",
) -> str:
    city = city.lower()
    state = (state or "").lower()
    country = (country or "US").lower()
    unit_group = unit_group.lower()
    return f"weather:{city}:{state}:{country}:{unit_group}"


def get_cached_weather(
    city: str,
    state: Optional[str] = None,
    country: str = "US",
    unit_group: str = "metric",
) -> Optional[Dict[str, Any]]:
    key = _make_cache_key(city, state, country, unit_group)
    cached_json = redis_client.get(key)
    if not cached_json:
        return None
    return json.loads(cached_json)


def set_cached_weather(
    city: str,
    data: Dict[str, Any],
    state: Optional[str] = None,
    country: str = "US",
    unit_group: str = "metric",
) -> None:
    key = _make_cache_key(city, state, country, unit_group)
    ttl = Config.CACHE_TTL_SECONDS
    redis_client.setex(key, ttl, json.dumps(data))


def _build_location_string(
    city: str,
    state: Optional[str] = None,
    country: str = "US",
) -> str:
    parts = [city]
    if state:
        parts.append(state)
    if country:
        parts.append(country)
    return ",".join(parts)


def fetch_weather_from_api(
    city: str,
    state: Optional[str] = None,
    country: str = "US",
    unit_group: str = "metric",
) -> Dict[str, Any]:
    if not Config.VISUAL_CROSSING_API_KEY:
        raise RuntimeError("Visual Crossing API key is not configured")

    location = _build_location_string(city, state, country)
    url = f"{Config.VISUAL_CROSSING_BASE_URL}/{location}"

    params = {
        "unitGroup": unit_group,
        "key": Config.VISUAL_CROSSING_API_KEY,
        "contentType": "json",
    }

    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code == 400:
        raise ValueError(f"Invalid location '{location}' or bad request")
    if resp.status_code >= 500:
        raise RuntimeError("Upstream weather service is unavailable")

    resp.raise_for_status()
    return resp.json()


def get_weather(
    city: str,
    state: Optional[str] = None,
    country: str = "US",
    unit_group: str = "metric",
    use_cache: bool = True,
) -> Dict[str, Any]:
    if use_cache:
        cached = get_cached_weather(city, state, country, unit_group)
        if cached is not None:
            return {"source": "cache", "data": cached}

    data = fetch_weather_from_api(city, state, country, unit_group)

    if use_cache:
        set_cached_weather(city, data, state, country, unit_group)

    return {"source": "api", "data": data}
