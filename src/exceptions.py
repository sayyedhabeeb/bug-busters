"""
Custom exception classes for the job recommendation system.

This module defines application-specific exceptions for better error handling
and more informative error messages throughout the system.
"""

from typing import Any, Dict, Optional


class RecommendationSystemException(Exception):
    """Base exception for all recommendation system errors."""
    
    def __init__(
        self, 
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        """
        Initialize exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            status_code: HTTP status code
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'status_code': self.status_code
        }


class ValidationError(RecommendationSystemException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            details=details or {},
            status_code=400
        )


class DataError(RecommendationSystemException):
    """Raised when data processing encounters errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='DATA_ERROR',
            details=details or {},
            status_code=422
        )


class ParseError(RecommendationSystemException):
    """Raised when resume/job parsing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='PARSE_ERROR',
            details=details or {},
            status_code=400
        )


class MatchingError(RecommendationSystemException):
    """Raised when matching operation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='MATCHING_ERROR',
            details=details or {},
            status_code=500
        )


class ModelError(RecommendationSystemException):
    """Raised when model inference fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='MODEL_ERROR',
            details=details or {},
            status_code=500
        )


class DatabaseError(RecommendationSystemException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='DATABASE_ERROR',
            details=details or {},
            status_code=500
        )


class ConfigurationError(RecommendationSystemException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='CONFIG_ERROR',
            details=details or {},
            status_code=500
        )


class ResourceNotFoundError(RecommendationSystemException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='NOT_FOUND',
            details=details or {},
            status_code=404
        )


class AuthenticationError(RecommendationSystemException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code='AUTH_ERROR',
            details={},
            status_code=401
        )


class AuthorizationError(RecommendationSystemException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code='FORBIDDEN',
            details={},
            status_code=403
        )


class RateLimitError(RecommendationSystemException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            error_code='RATE_LIMIT_EXCEEDED',
            details={'retry_after': retry_after},
            status_code=429
        )


class TimeoutError(RecommendationSystemException):
    """Raised when operation times out."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='TIMEOUT',
            details=details or {},
            status_code=504
        )


class ServiceUnavailableError(RecommendationSystemException):
    """Raised when a service is unavailable."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='SERVICE_UNAVAILABLE',
            details=details or {},
            status_code=503
        )


class BatchProcessingError(RecommendationSystemException):
    """Raised when batch processing encounters errors."""
    
    def __init__(
        self, 
        message: str,
        failed_count: int = 0,
        total_count: int = 0,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details.update({
            'failed_count': failed_count,
            'total_count': total_count
        })
        super().__init__(
            message=message,
            error_code='BATCH_ERROR',
            details=error_details,
            status_code=500
        )


class FeatureEngineeringError(RecommendationSystemException):
    """Raised when feature engineering fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='FEATURE_ERROR',
            details=details or {},
            status_code=500
        )


class ExplainabilityError(RecommendationSystemException):
    """Raised when explainability generation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code='EXPLAIN_ERROR',
            details=details or {},
            status_code=500
        )


class ExternalServiceError(RecommendationSystemException):
    """Raised when external service call fails."""
    
    def __init__(
        self,
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details['service'] = service_name
        super().__init__(
            message=message,
            error_code='EXTERNAL_SERVICE_ERROR',
            details=error_details,
            status_code=502
        )
