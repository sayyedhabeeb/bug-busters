import functools
from typing import Callable, Any
import threading
from cachetools import TTLCache, LRUCache

# 1. Simple LRU Cache Decorator
def lru_cache_with_ttl(maxsize: int = 128, ttl: int = 3600):
    """
    Decorator for LRU caching with Time-To-Live.
    Useful for database queries or API calls.
    """
    cache = TTLCache(maxsize=maxsize, ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a key based on args and kwargs
            key = str(args) + str(kwargs)
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator

# 2. Singleton Model Cache (Thread-Safe)
class ModelCache:
    """
    Singleton to hold heavy models in memory.
    Prevents reloading models on every request.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelCache, cls).__new__(cls)
                    cls._instance.models = {}
        return cls._instance
    
    def get(self, key: str) -> Any:
        return self.models.get(key)
    
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self.models[key] = value
            
    def clear(self):
        with self._lock:
            self.models.clear()

# Global Cache Instance
feature_cache = LRUCache(maxsize=1000)
