"""
Mobile-Only Authentication with Signup
- Mobile number registration with OTP verification
- Mobile-only login with OTP
- Industry-level session management
- Complete user profile during signup
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from .otp_service import otp_service
from .session_manager import session_manager
import logging
import re

logger = logging.getLogger(__name__)
User = get_user_model()


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):
    """Extract device information from request"""
    return {
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        'device_type': 'mobile' if 'Mobile' in request.META.get('HTTP_USER_AGENT', '') else 'desktop',
        'platform': request.META.get('HTTP_SEC_CH_UA_PLATFORM', 'Unknown'),
    }


def validate_mobile_number(mobile):
    """
    Validate mobile number format
    Expected: +[country_code][number] (e.g., +917012345678)
    """
    if not mobile:
        return False, "Mobile number is required"
    
    # Remove spaces and dashes
    mobile = mobile.replace(' ', '').replace('-', '')
    
    # Check format: +[1-3 digits country code][6-12 digits number]
    pattern = r'^\+\d{1,3}\d{6,12}$'
    if not re.match(pattern, mobile):
        return False, "Invalid mobile number format. Use +[country][number] (e.g., +917012345678)"
    
    return True, mobile


class SignupRequestView(APIView):
    """
    Step 1 of signup: Validate data and send OTP for mobile verification
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Request signup with mobile verification
        
        Required fields:
        - mobile_number (primary identifier)
        - first_name
        - last_name
        - village
        - role (farmer/admin/technician)
        
        Optional fields:
        - email
        - username (auto-generated if not provided)
        """
        try:
            # Extract data
            mobile_number = request.data.get('mobile_number', '').strip()
            first_name = request.data.get('first_name', '').strip()
            last_name = request.data.get('last_name', '').strip()
            village = request.data.get('village', '').strip()
            role = request.data.get('role', 'farmer').lower()
            email = request.data.get('email', '').strip()
            username = request.data.get('username', '').strip()
            
            # Validate required fields
            if not all([mobile_number, first_name, last_name, village]):
                return Response({
                    'success': False,
                    'error': 'Missing required fields: mobile_number, first_name, last_name, village'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate mobile number
            is_valid, mobile_or_error = validate_mobile_number(mobile_number)
            if not is_valid:
                return Response({
                    'success': False,
                    'error': mobile_or_error
                }, status=status.HTTP_400_BAD_REQUEST)
            mobile_number = mobile_or_error
            
            # Validate role
            valid_roles = ['farmer', 'admin', 'technician', 'operator']
            if role not in valid_roles:
                return Response({
                    'success': False,
                    'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if mobile number already exists
            if User.objects.filter(phone_number=mobile_number).exists():
                return Response({
                    'success': False,
                    'error': 'Mobile number already registered. Please login instead.'
                }, status=status.HTTP_409_CONFLICT)
            
            # Check if email already exists (if provided)
            if email and User.objects.filter(email=email).exists():
                return Response({
                    'success': False,
                    'error': 'Email already registered'
                }, status=status.HTTP_409_CONFLICT)
            
            # Generate username if not provided
            if not username:
                # Use first_name + last 4 digits of mobile
                base_username = f"{first_name.lower()}_{mobile_number[-4:]}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
            else:
                # Check if username already exists
                if User.objects.filter(username=username).exists():
                    return Response({
                        'success': False,
                        'error': 'Username already taken'
                    }, status=status.HTTP_409_CONFLICT)
            
            # Store signup data temporarily
            signup_key = f"signup_pending_{mobile_number}"
            signup_data = {
                'mobile_number': mobile_number,
                'first_name': first_name,
                'last_name': last_name,
                'village': village,
                'role': role,
                'email': email or f"{username}@grammeter.local",
                'username': username,
            }
            cache.set(signup_key, signup_data, timeout=600)  # 10 minutes
            
            # Send OTP
            otp_result = otp_service.send_otp(mobile_number, mobile_number)  # Use mobile as temp ID
            
            if not otp_result['success']:
                return Response({
                    'success': False,
                    'error': otp_result['message'],
                    'wait_time': otp_result.get('wait_time')
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            logger.info(f"Signup OTP sent to {mobile_number}")
            
            return Response({
                'success': True,
                'message': otp_result['message'],
                'mobile_number': mobile_number,
                'masked_mobile': f"***{mobile_number[-4:]}",
                'expires_in': otp_result.get('expires_in', 300),
                'otp': otp_result.get('otp')  # Development only
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Signup request error: {e}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignupVerifyView(APIView):
    """
    Step 2 of signup: Verify OTP and create user account
    """
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request):
        """
        Verify OTP and create user
        
        Required fields:
        - mobile_number
        - otp
        """
        try:
            mobile_number = request.data.get('mobile_number', '').strip()
            otp_code = request.data.get('otp', '').strip()
            
            if not mobile_number or not otp_code:
                return Response({
                    'success': False,
                    'error': 'Mobile number and OTP are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get signup data
            signup_key = f"signup_pending_{mobile_number}"
            signup_data = cache.get(signup_key)
            
            if not signup_data:
                return Response({
                    'success': False,
                    'error': 'Signup session expired. Please start signup again.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Verify OTP
            otp_result = otp_service.verify_otp(mobile_number, otp_code)
            
            if not otp_result['valid']:
                return Response({
                    'success': False,
                    'error': otp_result['message']
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Create user
            user = User.objects.create_user(
                username=signup_data['username'],
                email=signup_data['email'],
                first_name=signup_data['first_name'],
                last_name=signup_data['last_name'],
                phone_number=signup_data['mobile_number'],
                village=signup_data['village'],
                role=signup_data['role'],
                password=None  # No password for mobile-only auth
            )
            
            # Clear signup data
            cache.delete(signup_key)
            
            # Create session
            session_data = session_manager.create_session(
                user,
                device_info=get_device_info(request),
                ip_address=get_client_ip(request)
            )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"User {user.username} registered successfully")
            
            return Response({
                'success': True,
                'message': 'Account created successfully',
                'session': {
                    'session_id': session_data['session_id'],
                    'expires_at': session_data['expires_at']
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'mobile_number': user.phone_number,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'village': user.village,
                    'role': user.role
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Signup verification error: {e}")
            return Response({
                'success': False,
                'error': 'Failed to create account'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MobileLoginRequestView(APIView):
    """
    Step 1 of mobile login: Validate mobile number and send OTP
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Request login with mobile number
        
        Required fields:
        - mobile_number
        """
        try:
            mobile_number = request.data.get('mobile_number', '').strip()
            
            if not mobile_number:
                return Response({
                    'success': False,
                    'error': 'Mobile number is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate mobile number format
            is_valid, mobile_or_error = validate_mobile_number(mobile_number)
            if not is_valid:
                return Response({
                    'success': False,
                    'error': mobile_or_error
                }, status=status.HTTP_400_BAD_REQUEST)
            mobile_number = mobile_or_error
            
            # Check if user exists
            try:
                user = User.objects.get(phone_number=mobile_number)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Mobile number not registered. Please sign up first.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if not user.is_active:
                return Response({
                    'success': False,
                    'error': 'Account is disabled. Contact administrator.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Send OTP
            otp_result = otp_service.send_otp(mobile_number, user.id)
            
            if not otp_result['success']:
                return Response({
                    'success': False,
                    'error': otp_result['message'],
                    'wait_time': otp_result.get('wait_time')
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Store temporary login data
            login_key = f"login_pending_{user.id}"
            cache.set(login_key, {
                'user_id': user.id,
                'mobile_number': mobile_number,
                'timestamp': otp_result.get('timestamp')
            }, timeout=300)
            
            logger.info(f"Login OTP sent to {mobile_number}")
            
            return Response({
                'success': True,
                'message': otp_result['message'],
                'user_id': user.id,
                'masked_mobile': f"***{mobile_number[-4:]}",
                'expires_in': otp_result.get('expires_in', 300),
                'otp': otp_result.get('otp')  # Development only
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Mobile login request error: {e}")
            return Response({
                'success': False,
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MobileLoginVerifyView(APIView):
    """
    Step 2 of mobile login: Verify OTP and create session
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Verify OTP and login
        
        Required fields:
        - user_id
        - otp
        """
        try:
            user_id = request.data.get('user_id')
            otp_code = request.data.get('otp', '').strip()
            
            if not user_id or not otp_code:
                return Response({
                    'success': False,
                    'error': 'User ID and OTP are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check login session
            login_key = f"login_pending_{user_id}"
            login_data = cache.get(login_key)
            
            if not login_data:
                return Response({
                    'success': False,
                    'error': 'Login session expired. Please request OTP again.'
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
            
            # Clear login data
            cache.delete(login_key)
            
            # Create session with device tracking
            session_data = session_manager.create_session(
                user,
                device_info=get_device_info(request),
                ip_address=get_client_ip(request)
            )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update last login
            user.last_login = user.last_login
            user.save(update_fields=['last_login'])
            
            logger.info(f"User {user.username} logged in successfully")
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'session': {
                    'session_id': session_data['session_id'],
                    'created_at': session_data['created_at'],
                    'expires_at': session_data['expires_at'],
                    'device_info': session_data['device_info'],
                    'location': session_data['location']
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'mobile_number': user.phone_number,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'village': user.village,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Mobile login verification error: {e}")
            return Response({
                'success': False,
                'error': 'Login failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    """
    Logout with session revocation
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Logout user and revoke session
        
        Optional fields:
        - session_id (specific session to revoke)
        - revoke_all (revoke all sessions)
        - refresh (JWT refresh token to blacklist)
        """
        try:
            session_id = request.data.get('session_id')
            revoke_all = request.data.get('revoke_all', False)
            refresh_token = request.data.get('refresh')
            
            # Revoke session(s)
            if revoke_all:
                count = session_manager.revoke_all_user_sessions(request.user.id)
                message = f"All {count} sessions revoked"
            elif session_id:
                session_manager.revoke_session(session_id)
                message = "Session revoked successfully"
            else:
                # Try to revoke current session (if session_id in request headers)
                session_id = request.headers.get('X-Session-ID')
                if session_id:
                    session_manager.revoke_session(session_id)
                message = "Logout successful"
            
            # Blacklist JWT refresh token
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    logger.warning(f"Failed to blacklist token: {e}")
            
            logger.info(f"User {request.user.username} logged out")
            
            return Response({
                'success': True,
                'message': message
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response({
                'success': False,
                'error': 'Logout failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SessionListView(APIView):
    """
    Get list of active sessions for current user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all active sessions"""
        try:
            sessions = session_manager.get_user_sessions(request.user.id)
            
            # Format session data
            formatted_sessions = []
            for session in sessions:
                formatted_sessions.append({
                    'session_id': session['session_id'],
                    'created_at': session['created_at'],
                    'last_activity': session['last_activity'],
                    'expires_at': session['expires_at'],
                    'device_info': session.get('device_info', {}),
                    'location': session.get('location', {}),
                    'ip_address': session.get('ip_address', 'unknown'),
                    'is_current': session['session_id'] == request.headers.get('X-Session-ID')
                })
            
            return Response({
                'success': True,
                'count': len(formatted_sessions),
                'sessions': formatted_sessions
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Session list error: {e}")
            return Response({
                'success': False,
                'error': 'Failed to fetch sessions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP for signup or login
    """
    try:
        mobile_number = request.data.get('mobile_number', '').strip()
        purpose = request.data.get('purpose', 'login')  # 'login' or 'signup'
        
        if not mobile_number:
            return Response({
                'success': False,
                'error': 'Mobile number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate mobile
        is_valid, mobile_or_error = validate_mobile_number(mobile_number)
        if not is_valid:
            return Response({
                'success': False,
                'error': mobile_or_error
            }, status=status.HTTP_400_BAD_REQUEST)
        mobile_number = mobile_or_error
        
        # Determine identifier for OTP
        if purpose == 'signup':
            identifier = mobile_number
        else:
            # For login, use user_id
            try:
                user = User.objects.get(phone_number=mobile_number)
                identifier = user.id
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Mobile number not registered'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Send OTP
        otp_result = otp_service.send_otp(mobile_number, identifier)
        
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
            'otp': otp_result.get('otp')  # Development only
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Resend OTP error: {e}")
        return Response({
            'success': False,
            'error': 'Failed to resend OTP'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
