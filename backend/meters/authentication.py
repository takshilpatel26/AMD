"""
Custom JWT Authentication that reads tokens from httpOnly cookies
instead of Authorization headers for enhanced security
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class that extracts the token from cookies
    instead of the Authorization header.
    
    This provides better security by:
    1. Preventing XSS attacks (JavaScript cannot access httpOnly cookies)
    2. Automatic token inclusion in requests (no manual header management)
    3. Better CSRF protection with SameSite cookie attribute
    """

    def authenticate(self, request):
        """
        Try to authenticate using cookie-based JWT token first,
        fall back to header-based authentication for API clients
        """
        # First, try to get token from cookie (preferred method)
        cookie_token = request.COOKIES.get('access_token')
        
        if cookie_token:
            try:
                validated_token = self.get_validated_token(cookie_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, AuthenticationFailed):
                # Cookie token is invalid, try header authentication
                pass
        
        # Fall back to standard header-based authentication
        # This allows API clients (like Postman) to still use Bearer tokens
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
