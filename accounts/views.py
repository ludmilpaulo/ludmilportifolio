from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json
import random
import re
import string
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .models import CustomUser, PasswordResetToken, UserProfile, LoginLog
from .serializers import (
    CustomUserSerializer, LoginSerializer, RegisterSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
    ChangePasswordSerializer, UserProfileSerializer, LoginLogSerializer
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """User login with token authentication"""
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            # Log login activity
            LoginLog.objects.create(
                user=user,
                ip_address=(
                    request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                    or request.META.get('REMOTE_ADDR', '')
                    or '0.0.0.0'
                ),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_successful=True
            )
            
            user_serializer = CustomUserSerializer(user)
            return Response({
                'success': True,
                'token': token.key,
                'user': user_serializer.data
            })
        else:
            # Extract error details from serializer
            error_data = serializer.errors
            error_message = 'Invalid credentials'
            error_code = 'invalid_credentials'
            
            # Get error from non_field_errors (from validate method)
            if 'non_field_errors' in error_data:
                error_detail = error_data['non_field_errors'][0]
                error_message = str(error_detail)
                
                # Determine error code from message content (fallback method)
                error_lower = error_message.lower()
                if 'does not exist' in error_lower or 'user or email' in error_lower:
                    error_code = 'user_not_found'
                elif 'password' in error_lower and ('incorrect' in error_lower or 'wrong' in error_lower):
                    error_code = 'wrong_password'
                elif 'disabled' in error_lower:
                    error_code = 'account_disabled'
            
            return Response({
                'success': False, 
                'error': error_message,
                'error_code': error_code
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            'success': False, 
            'error': str(e),
            'error_code': 'server_error'
        }, status=status.HTTP_400_BAD_REQUEST)


def _client_ip(request):
    return (
        request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        or request.META.get('REMOTE_ADDR', '')
        or '0.0.0.0'
    )


def _login_payload(request, user):
    token, _created = Token.objects.get_or_create(user=user)
    LoginLog.objects.create(
        user=user,
        ip_address=_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        is_successful=True,
    )
    return {
        'success': True,
        'token': token.key,
        'user': CustomUserSerializer(user).data,
    }


def _verify_google_id_token(credential, client_id):
    query = urlencode({'id_token': credential})
    req = Request(
        f'https://oauth2.googleapis.com/tokeninfo?{query}',
        headers={'Accept': 'application/json'},
    )
    try:
        with urlopen(req, timeout=10) as response:
            payload = json.loads(response.read().decode())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValueError('invalid_token') from exc

    if not isinstance(payload, dict):
        raise ValueError('invalid_token')
    if payload.get('aud') != client_id:
        raise ValueError('wrong_audience')
    if str(payload.get('iss')) not in ('accounts.google.com', 'https://accounts.google.com'):
        raise ValueError('invalid_issuer')
    if str(payload.get('email_verified')).lower() != 'true':
        raise ValueError('email_unverified')
    email = str(payload.get('email') or '').strip().lower()
    if not email or '@' not in email:
        raise ValueError('email_missing')
    payload['email'] = email
    return payload


def _username_from_email(email):
    local = email.split('@', 1)[0].lower()
    base = re.sub(r'[^a-z0-9_]', '', local)[:20] or 'client'
    candidate = base
    suffix = 1
    while CustomUser.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = f'{base}{suffix}'[:150]
    return candidate


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_login(request):
    """Sign in with a Google ID token. New accounts are clients, never admins."""
    client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '') or ''
    if not client_id:
        return Response(
            {'success': False, 'error': 'Google sign-in is not configured', 'error_code': 'google_not_configured'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    credential = str(request.data.get('credential') or '').strip()
    role = str(request.data.get('role') or 'client').strip().lower()
    if role not in ('admin', 'client'):
        role = 'client'
    if not credential:
        return Response(
            {'success': False, 'error': 'Google credential is required', 'error_code': 'invalid_token'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        profile = _verify_google_id_token(credential, client_id)
    except ValueError as exc:
        code = str(exc)
        message = 'Google sign-in could not be verified. Please try again.'
        if code == 'email_unverified':
            message = 'That Google account has not verified its email address.'
        return Response(
            {'success': False, 'error': message, 'error_code': code},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    email = profile['email']
    user = CustomUser.objects.filter(email__iexact=email).first()
    if user is None and role == 'admin':
        return Response(
            {
                'success': False,
                'error': 'No admin account uses this Google email.',
                'error_code': 'not_admin',
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    if user is not None and role == 'admin' and user.user_type != 'admin':
        return Response(
            {
                'success': False,
                'error': 'This Google account is not an admin.',
                'error_code': 'not_admin',
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    if user is not None and role == 'client' and user.user_type != 'client':
        return Response(
            {
                'success': False,
                'error': 'This Google account is an admin. Use the admin sign-in.',
                'error_code': 'use_admin_login',
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    if user is not None and not user.is_active:
        return Response(
            {'success': False, 'error': 'This account is disabled.', 'error_code': 'account_disabled'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if user is None:
        user = CustomUser(
            username=_username_from_email(email),
            email=email,
            first_name=str(profile.get('given_name') or '')[:150],
            last_name=str(profile.get('family_name') or '')[:150],
            user_type='client',
            is_verified=True,
        )
        user.set_unusable_password()
        user.save()

    return Response(_login_payload(request, user))


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_register(request):
    """User registration"""
    try:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_serializer = CustomUserSerializer(user)
            return Response({
                'success': True,
                'user': user_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    """Send password reset email"""
    try:
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = CustomUser.objects.get(email=email)
                
                # Create password reset token
                expires_at = timezone.now() + timezone.timedelta(hours=24)
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    expires_at=expires_at
                )
                
                # Send email
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response({
                    'success': True, 
                    'message': 'Password reset email sent'
                })
            except CustomUser.DoesNotExist:
                return Response({
                    'success': False, 
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False, 
                'error': 'Invalid email'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False, 
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """Reset password using token"""
    try:
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
                
                if reset_token.is_expired():
                    return Response({
                        'success': False, 
                        'error': 'Token expired'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update password
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Mark token as used
                reset_token.is_used = True
                reset_token.save()
                
                return Response({
                    'success': True, 
                    'message': 'Password reset successfully'
                })
            except PasswordResetToken.DoesNotExist:
                return Response({
                    'success': False, 
                    'error': 'Invalid token'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False, 
                'error': 'Invalid data'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False, 
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password"""
    try:
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            user = request.user
            if not user.check_password(old_password):
                return Response({
                    'success': False,
                    'error': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    try:
        user_serializer = CustomUserSerializer(request.user)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_serializer = UserProfileSerializer(profile)
        
        return Response({
            'success': True,
            'user': user_serializer.data,
            'profile': profile_serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request):
    """Update user profile"""
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Update user fields
        user_data = request.data.get('user', {})
        for field in ['first_name', 'last_name', 'phone', 'company']:
            if field in user_data:
                setattr(user, field, user_data[field])
        user.save()
        
        # Update profile fields
        profile_data = request.data.get('profile', {})
        profile_serializer = UserProfileSerializer(profile, data=profile_data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
        
        user_serializer = CustomUserSerializer(user)
        return Response({
            'success': True,
            'user': user_serializer.data,
            'profile': profile_serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def user_logout(request):
    """User logout"""
    try:
        # Delete token
        Token.objects.filter(user=request.user).delete()
        
        # Log logout activity
        LoginLog.objects.filter(
            user=request.user,
            logout_time__isnull=True
        ).update(logout_time=timezone.now())
        
        logout(request)
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_login_history(request):
    """Get user login history"""
    try:
        logs = LoginLog.objects.filter(user=request.user)[:50]  # Last 50 logins
        serializer = LoginLogSerializer(logs, many=True)
        
        return Response({
            'success': True,
            'logs': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_token(request):
    """Verify the validity of an authentication token"""
    token_key = request.data.get('token')

    if not token_key:
        return Response({
            'success': False,
            'error': 'Token is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = Token.objects.select_related('user').get(key=token_key)

        if not token.user.is_active:
            return Response({
                'success': False,
                'error': 'User account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'success': True,
            'valid': True,
            'user_type': token.user.user_type
        })
    except Token.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_user_by_token(request):
    """Retrieve user details associated with a token"""
    token_key = request.data.get('token')

    if not token_key:
        return Response({
            'success': False,
            'error': 'Token is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = Token.objects.select_related('user').get(key=token_key)

        if not token.user.is_active:
            return Response({
                'success': False,
                'error': 'User account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)

        user_serializer = CustomUserSerializer(token.user)
        return Response(user_serializer.data)
    except Token.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid token'
        }, status=status.HTTP_401_UNAUTHORIZED)


def generate_client_credentials():
    """Generate random username and password for client"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return username, password
