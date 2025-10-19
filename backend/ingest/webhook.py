import requests
from utils.logger import logger


def notify_cache_expiry(cache_key_param: str) -> bool:
    """
    Send webhook notification to expire a cache key.

    Args:
        cache_key_param (str): Redis cache key to expire
        
    Returns:
        bool: True if webhook succeeded, False otherwise
    """
    try:
        resp = requests.post(
            "http://localhost:8000/expire_cache/",
            json={"cache_key": cache_key_param},
            timeout=5  # Increased timeout for reliability
        )

        if resp.status_code == 200:
            logger.info(f"Webhook success: {resp.json().get('message', 'Cache expired')}")
            return True
        else:
            logger.error(f"Webhook failed with status {resp.status_code}")
            return False
            
    except (requests.RequestException, ValueError, TypeError) as e:
        logger.warning(f"Webhook error: {e}")
        return False