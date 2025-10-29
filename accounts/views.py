from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
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
                ip_address=request.META.get('REMOTE_ADDR', ''),
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


def generate_client_credentials():
    """Generate random username and password for client"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return username, password
