"""
Caching and performance optimization module.

Implements multiple caching strategies including in-memory, Redis, and file-based
caching with automatic invalidation and monitoring.
"""

import hashlib
import json
import pickle
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from functools import wraps
import logging

try:
    import redis
except ImportError:
    redis = None


logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache implementations."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass


class InMemoryCache(CacheBackend):
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize in-memory cache.
        
        Args:
            max_size: Maximum number of items in cache
        """
        self.cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value with TTL checking."""
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, expiry = self.cache[key]
        
        if expiry is not None and time.time() > expiry:
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value with optional TTL."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        expiry = time.time() + ttl if ttl else None
        self.cache[key] = (value, expiry)
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        self.cache.clear()
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache),
            'max_size': self.max_size
        }


class FileCache(CacheBackend):
    """File-based cache with JSON and pickle support."""
    
    def __init__(self, cache_dir: Path = Path('cache'), serializer: str = 'pickle'):
        """
        Initialize file cache.
        
        Args:
            cache_dir: Directory to store cache files
            serializer: 'pickle' or 'json'
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.serializer = serializer
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        # Hash key to create valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        ext = 'pkl' if self.serializer == 'pickle' else 'json'
        return self.cache_dir / f"{key_hash}.{ext}"
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from file."""
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return None
        
        try:
            if self.serializer == 'pickle':
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
            else:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
            
            # Check TTL
            if 'expiry' in data and time.time() > data['expiry']:
                cache_file.unlink()
                return None
            
            return data.get('value')
        
        except Exception as e:
            logger.error(f"Error reading cache file {cache_file}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value to file."""
        cache_file = self._get_cache_file(key)
        
        try:
            data = {
                'value': value,
                'expiry': time.time() + ttl if ttl else None
            }
            
            if self.serializer == 'pickle':
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            else:
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
            
            return True
        
        except Exception as e:
            logger.error(f"Error writing cache file {cache_file}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cache file."""
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cache files."""
        try:
            for cache_file in self.cache_dir.glob('*'):
                cache_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if cache file exists."""
        return self._get_cache_file(key).exists()


class RedisCache(CacheBackend):
    """Redis-based distributed cache."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
        """
        if redis is None:
            raise ImportError("redis package required for RedisCache")
        
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.prefix = "rec_sys:"
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from Redis."""
        try:
            value = self.client.get(self._make_key(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in Redis."""
        try:
            self.client.set(
                self._make_key(key),
                json.dumps(value),
                ex=ttl
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            return bool(self.client.delete(self._make_key(key)))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cached keys."""
        try:
            for key in self.client.scan_iter(f"{self.prefix}*"):
                self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.client.exists(self._make_key(key)))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False


class CacheManager:
    """Unified cache management with multiple backends."""
    
    def __init__(self, backend: CacheBackend = None):
        """
        Initialize cache manager.
        
        Args:
            backend: Cache backend to use (defaults to InMemoryCache)
        """
        self.backend = backend or InMemoryCache()
    
    def get(self, key: str, compute_fn=None, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get value from cache or compute if missing.
        
        Args:
            key: Cache key
            compute_fn: Function to compute value if cache miss
            ttl: Time to live in seconds
        
        Returns:
            Cached or computed value
        """
        cached = self.backend.get(key)
        
        if cached is not None:
            logger.debug(f"Cache hit: {key}")
            return cached
        
        if compute_fn is None:
            return None
        
        logger.debug(f"Cache miss: {key}, computing value")
        value = compute_fn()
        self.backend.set(key, value, ttl)
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value."""
        return self.backend.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete cache key."""
        return self.backend.delete(key)
    
    def clear(self) -> bool:
        """Clear all cache."""
        return self.backend.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.backend.exists(key)


def cached(ttl: Optional[int] = None, backend: Optional[CacheBackend] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        backend: Cache backend to use
    
    Example:
        @cached(ttl=3600)
        def expensive_operation(x, y):
            return x + y
    """
    cache_mgr = CacheManager(backend or InMemoryCache())
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            return cache_mgr.get(
                key,
                compute_fn=lambda: func(*args, **kwargs),
                ttl=ttl
            )
        
        return wrapper
    
    return decorator


# Global cache instance
_global_cache: Optional[CacheManager] = None


def get_cache(backend: Optional[CacheBackend] = None) -> CacheManager:
    """Get or create global cache manager."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager(backend or InMemoryCache())
    return _global_cache
