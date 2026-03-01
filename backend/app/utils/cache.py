import json
import logging
from typing import Any, Optional
from app import extensions 
from flask import current_app
from app.config import Config


logger = logging.getLogger(__name__)
SHORT_TTL = Config.SHORT_TTL
MEDIUM_TTL = Config.MEDIUM_TTL
LONG_TTL = Config.LONG_TTL

def build_cache_key(*parts) -> str:
    return "hms:" + ":".join(str(part) for part in parts)

def cache_get(key:str) -> Optional[Any]:
    try:
        cached_value = extensions.redis_client.get(key)
        if cached_value is None:
            return None
        
        return json.loads(cached_value)
    
    except Exception as exc:
        logger.warning(f"Redis GET failed for key={key}: {exc}")
        return None
    
def cache_set(key:str, value:Any, ttl: int | None=None) -> None:
    if extensions.redis_client is None:
        return
    try:
        serialized_value = json.dumps(value)
        ttl=ttl or current_app.config.get("CACHE_TTLMEDIUM", 600)
        extensions.redis_client.setex(key, ttl, serialized_value)

    except Exception as exc:
        logger.warning(f"Redis SET failed for key={key}: {exc}")

def cache_delete(key:str) -> None:

    try:
        if extensions.redis_client is None:
            return None
        extensions.redis_client.delete(key)

    except Exception as exc:
        logger.warning(f"Redis DELETE failed for key={key}: {exc}")
