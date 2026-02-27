"""
Secure Authentication Views with httpOnly Cookie-based JWT Storage
Industry-standard security practices for token management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.conf import settings
from datetime import timedelta


@api_view(['POST'])
@permission_classes([AllowAny])
def secure_login(request):
    """
    Secure login endpoint that stores JWT tokens in httpOnly cookies
    to prevent XSS attacks. Tokens are NOT exposed to JavaScript.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    remember_me = request.data.get('remember_me', False)

    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Create response
    response = Response({
        'success': True,
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
        }
    }, status=status.HTTP_200_OK)

    # Calculate cookie expiration based on remember_me
    if remember_me:
        access_max_age = 30 * 24 * 60 * 60  # 30 days
        refresh_max_age = 90 * 24 * 60 * 60  # 90 days
    else:
        access_max_age = 60 * 60  # 1 hour
        refresh_max_age = 24 * 60 * 60  # 24 hours

    # Set secure httpOnly cookies
    response.set_cookie(
        key='access_token',
        value=access_token,
        max_age=access_max_age,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite='Lax',  # CSRF protection
        path='/'
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        path='/'
    )

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def secure_refresh(request):
    """
    Refresh access token using the refresh token from httpOnly cookie
    """
    refresh_token = request.COOKIES.get('refresh_token')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token not found'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)

        response = Response({
            'success': True,
            'message': 'Token refreshed successfully'
        }, status=status.HTTP_200_OK)

        # Set new access token cookie
        response.set_cookie(
            key='access_token',
            value=access_token,
            max_age=60 * 60,  # 1 hour
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            path='/'
        )

        return response

    except TokenError as e:
        return Response(
            {'error': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def secure_logout(request):
    """
    Secure logout that blacklists the refresh token and clears all cookies
    """
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token

        response = Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)

        # Delete all authentication cookies
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')

        return response

    except Exception as e:
        # Even if blacklisting fails, clear cookies
        response = Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify if the current token is valid and return user info
    """
    user = request.user
    
    return Response({
        'valid': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_status(request):
    """
    Check authentication status without requiring authentication
    Useful for checking if user is logged in on app load
    """
    access_token = request.COOKIES.get('access_token')
    
    return Response({
        'authenticated': bool(access_token),
        'has_token': bool(access_token)
    }, status=status.HTTP_200_OK)
