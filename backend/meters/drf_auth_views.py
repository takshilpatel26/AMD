"""
Django REST Framework Authentication API with JWT + 2FA OTP
Clean separation of frontend and backend with secure token-based auth
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from .otp_service import otp_service
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class LoginRequestView(APIView):
    """
    Step 1 of 2FA login: Validate credentials and send OTP
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authenticate user and send OTP to registered phone
        
        Request body:
        {
            "username": "farmer_ramesh",
            "password": "password123"
        }
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            logger.warning(f"Failed login attempt for username: {username}")
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'error': 'Account is disabled'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user has phone number
        if not user.phone_number:
            return Response({
                'success': False,
                'error': 'No phone number registered. Please contact administrator.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send OTP
        otp_result = otp_service.send_otp(user.phone_number, user.id)
        
        if not otp_result['success']:
            return Response({
                'success': False,
                'error': otp_result['message'],
                'wait_time': otp_result.get('wait_time')
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Store user ID temporarily for OTP verification
        temp_key = f"login_pending_{user.id}"
        cache.set(temp_key, {
            'user_id': user.id,
            'username': user.username,
            'timestamp': str(user.last_login)
        }, timeout=300)  # 5 minutes
        
        logger.info(f"OTP sent successfully to user: {username}")
        
        return Response({
            'success': True,
            'message': otp_result['message'],
            'user_id': user.id,
            'phone_number_masked': f"***{user.phone_number[-4:]}",
            'expires_in': otp_result.get('expires_in', 300),
            'otp': otp_result.get('otp')  # Only for testing - remove in production
        }, status=status.HTTP_200_OK)


class LoginVerifyView(APIView):
    """
    Step 2 of 2FA login: Verify OTP and issue JWT tokens
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Verify OTP and return JWT tokens
        
        Request body:
        {
            "user_id": 1,
            "otp": "123456"
        }
        """
        user_id = request.data.get('user_id')
        otp_code = request.data.get('otp')
        
        if not user_id or not otp_code:
            return Response({
                'success': False,
                'error': 'Please provide user_id and OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if login request exists
        temp_key = f"login_pending_{user_id}"
        login_data = cache.get(temp_key)
        
        if not login_data:
            return Response({
                'success': False,
                'error': 'Login session expired. Please start login again.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verify OTP
        otp_result = otp_service.verify_otp(user_id, otp_code)
        
        if not otp_result['valid']:
            return Response({
                'success': False,
                'error': otp_result['message']
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Clear temporary login data
        cache.delete(temp_key)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Update last login
        user.last_login = user.last_login
        user.save(update_fields=['last_login'])
        
        logger.info(f"User {user.username} logged in successfully with 2FA")
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'tokens': {
                'access': access_token,
                'refresh': refresh_token
            },
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'role': user.role,
                'village': user.village
            }
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    Resend OTP for pending login
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Resend OTP to user
        
        Request body:
        {
            "user_id": 1
        }
        """
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'error': 'Please provide user_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if login request exists
        temp_key = f"login_pending_{user_id}"
        login_data = cache.get(temp_key)
        
        if not login_data:
            return Response({
                'success': False,
                'error': 'Login session expired. Please start login again.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Send new OTP
        otp_result = otp_service.send_otp(user.phone_number, user.id)
        
        if not otp_result['success']:
            return Response({
                'success': False,
                'error': otp_result['message'],
                'wait_time': otp_result.get('wait_time')
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return Response({
            'success': True,
            'message': otp_result['message'],
            'expires_in': otp_result.get('expires_in', 300),
            'otp': otp_result.get('otp')  # Only for testing
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logout and blacklist refresh token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Blacklist refresh token to invalidate it
        
        Request body:
        {
            "refresh": "refresh_token_here"
        }
        """
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'success': False,
                'error': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User {request.user.username} logged out successfully")
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except TokenError as e:
            return Response({
                'success': False,
                'error': 'Invalid or expired refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)


class TokenRefreshAPIView(TokenRefreshView):
    """
    Custom token refresh view with better response format
    """
    
    def post(self, request, *args, **kwargs):
        """
        Refresh access token using refresh token
        
        Request body:
        {
            "refresh": "refresh_token_here"
        }
        """
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            return Response({
                'success': True,
                'tokens': {
                    'access': response.data.get('access'),
                    'refresh': response.data.get('refresh')
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': 'Token refresh failed'
        }, status=response.status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify if current access token is valid
    """
    return Response({
        'success': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'role': request.user.role
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_status(request):
    """
    Get current authentication status and user details
    """
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone_number': request.user.phone_number,
            'role': request.user.role,
            'village': request.user.village,
            'date_joined': request.user.date_joined
        }
    }, status=status.HTTP_200_OK)
