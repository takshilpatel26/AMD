"""
Custom Exception Handlers - Centralized error handling
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    Provides consistent error response format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize error response format
        error_response = {
            'success': False,
            'error': {
                'message': str(exc),
                'type': exc.__class__.__name__,
                'status_code': response.status_code
            }
        }
        
        # Add field errors if present
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                error_response['error']['fields'] = exc.detail
            else:
                error_response['error']['details'] = exc.detail
        
        response.data = error_response
        
        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            extra={'context': context, 'response': response.data}
        )
    
    return response


class GramMeterException(Exception):
    """Base exception for Gram Meter application"""
    default_message = "An error occurred in Gram Meter"
    
    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class MeterNotFoundException(GramMeterException):
    """Raised when a meter is not found"""
    default_message = "Meter not found"


class InvalidReadingException(GramMeterException):
    """Raised when a meter reading is invalid"""
    default_message = "Invalid meter reading"


class InsufficientDataException(GramMeterException):
    """Raised when there's not enough data for analysis"""
    default_message = "Insufficient data for analysis"


class MLModelException(GramMeterException):
    """Raised when ML model operations fail"""
    default_message = "ML model operation failed"
