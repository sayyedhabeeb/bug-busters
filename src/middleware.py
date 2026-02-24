"""
API middleware and interceptor layer.

Provides request/response processing, rate limiting, authentication, and logging.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

from flask import request, jsonify, g

logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


class RequestLogger:
    """Logs HTTP requests with detailed information."""
    
    @staticmethod
    def log_request(request_obj=None):
        """Log incoming request."""
        if request_obj is None:
            request_obj = request
        
        logger.info(
            f"HTTP {request_obj.method} {request_obj.path}",
            extra={
                'extra_data': {
                    'method': request_obj.method,
                    'path': request_obj.path,
                    'remote_addr': request_obj.remote_addr,
                    'user_agent': request_obj.user_agent.string,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        )
    
    @staticmethod
    def log_response(status_code: int, duration: float):
        """Log response."""
        logger.info(
            f"HTTP Response {status_code}",
            extra={
                'extra_data': {
                    'status_code': status_code,
                    'duration_ms': duration * 1000,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        )


class RequestContext:
    """Manages request-scoped context."""
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set context value."""
        if not hasattr(g, 'context'):
            g.context = {}
        g.context[key] = value
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get context value."""
        if not hasattr(g, 'context'):
            return default
        return g.context.get(key, default)
    
    @staticmethod
    def clear() -> None:
        """Clear context."""
        if hasattr(g, 'context'):
            g.context = {}


class RateLimiter:
    """Rate limiting for API endpoints."""
    
    def __init__(self, max_requests: int = 100, window_size: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests in window
            window_size: Window size in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests: Dict[str, list] = {}  # {client_id: [timestamps]}
    
    def _get_client_id(self) -> str:
        """Get client identifier."""
        # Try to use API key, fall back to IP
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return api_key
        return request.remote_addr or 'unknown'
    
    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        client_id = self._get_client_id()
        now = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside window
        self.requests[client_id] = [
            ts for ts in self.requests[client_id]
            if now - ts < self.window_size
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self) -> int:
        """Get remaining requests in current window."""
        client_id = self._get_client_id()
        now = time.time()
        
        if client_id not in self.requests:
            return self.max_requests
        
        valid_requests = [
            ts for ts in self.requests[client_id]
            if now - ts < self.window_size
        ]
        
        return max(0, self.max_requests - len(valid_requests))
    
    def get_reset_time(self) -> Optional[datetime]:
        """Get when rate limit resets."""
        client_id = self._get_client_id()
        
        if not self.requests.get(client_id):
            return None
        
        oldest = min(self.requests[client_id])
        reset = oldest + self.window_size
        return datetime.fromtimestamp(reset)


class ResponseInterceptor:
    """Intercepts and modifies responses."""
    
    @staticmethod
    def add_headers(response: Any, headers: Dict[str, str]) -> Any:
        """Add headers to response."""
        for key, value in headers.items():
            response.headers[key] = value
        return response
    
    @staticmethod
    def add_metadata(data: Dict[str, Any], **metadata) -> Dict[str, Any]:
        """Add metadata to response."""
        return {
            **data,
            '_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.0',
                **metadata
            }
        }


def rate_limit(max_requests: int = 100, window_size: int = 60):
    """
    Decorator for rate limiting.
    
    Args:
        max_requests: Maximum requests in window
        window_size: Window size in seconds
    
    Example:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_size=60)
        def endpoint():
            pass
    """
    limiter = RateLimiter(max_requests, window_size)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.is_allowed():
                logger.warning(
                    f"Rate limit exceeded for {request.remote_addr}",
                    extra={'extra_data': {'client': request.remote_addr}}
                )
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': limiter.window_size
                }), 429
            
            # Add rate limit headers
            remaining = limiter.get_remaining()
            reset_time = limiter.get_reset_time()
            
            result = func(*args, **kwargs)
            
            if isinstance(result, tuple):
                response, status = result
                response.headers['X-RateLimit-Limit'] = str(limiter.max_requests)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                if reset_time:
                    response.headers['X-RateLimit-Reset'] = str(int(reset_time.timestamp()))
                return response, status
            
            return result
        
        return wrapper
    
    return decorator


def request_logger_middleware(func):
    """
    Decorator to log requests and responses.
    
    Example:
        @app.route('/api/endpoint')
        @request_logger_middleware
        def endpoint():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        RequestLogger.log_request()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            status_code = 200
            
            if isinstance(result, tuple) and len(result) >= 2:
                status_code = result[1]
            
            duration = time.time() - start_time
            RequestLogger.log_response(status_code, duration)
            
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    'extra_data': {
                        'duration_ms': duration * 1000,
                        'error': str(e)
                    }
                }
            )
            raise
    
    return wrapper


def validate_json(func):
    """
    Decorator to validate JSON request body.
    
    Example:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_json
        def endpoint():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({
                    'error': 'Request must be JSON',
                    'content_type': request.content_type
                }), 400
            
            if request.data and not request.json:
                return jsonify({
                    'error': 'Invalid JSON',
                }), 400
        
        return func(*args, **kwargs)
    
    return wrapper


def require_headers(*required_headers):
    """
    Decorator to require specific headers.
    
    Args:
        required_headers: Header names to require
    
    Example:
        @app.route('/api/endpoint')
        @require_headers('X-API-Key', 'X-Request-ID')
        def endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            missing = []
            
            for header in required_headers:
                if header not in request.headers:
                    missing.append(header)
            
            if missing:
                return jsonify({
                    'error': 'Missing required headers',
                    'missing_headers': missing
                }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def timeout_handler(seconds: int = 30):
    """
    Decorator to handle request timeouts.
    
    Args:
        seconds: Timeout in seconds
    
    Example:
        @app.route('/api/endpoint')
        @timeout_handler(seconds=30)
        def endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            elapsed = time.time() - start_time
            if elapsed > seconds:
                logger.warning(
                    f"Request timeout: {elapsed:.2f}s > {seconds}s",
                    extra={'extra_data': {'elapsed': elapsed, 'timeout': seconds}}
                )
            
            return result
        
        return wrapper
    
    return decorator


def add_response_metadata(func):
    """
    Decorator to add metadata to response.
    
    Example:
        @app.route('/api/endpoint')
        @add_response_metadata
        def endpoint():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        if isinstance(result, dict):
            return ResponseInterceptor.add_metadata(
                result,
                function=func.__name__,
                duration_ms=0
            )
        
        return result
    
    return wrapper
