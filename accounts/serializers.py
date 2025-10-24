from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import CustomUser, PasswordResetToken, UserProfile, LoginLog, ClientAccount


class CustomUserSerializer(serializers.ModelSerializer):
    """Custom User Serializer"""
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'user_type', 'phone', 'company', 'is_verified', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """User Profile Serializer"""
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Login Request Serializer"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class RegisterSerializer(serializers.ModelSerializer):
    """User Registration Serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'password', 'password_confirm', 'user_type', 
            'phone', 'company'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot Password Request Serializer"""
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """Reset Password Serializer"""
    token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Change Password Serializer"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    """Password Reset Token Serializer"""
    class Meta:
        model = PasswordResetToken
        fields = ['token', 'created_at', 'expires_at']


class LoginLogSerializer(serializers.ModelSerializer):
    """Login Log Serializer"""
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = LoginLog
        fields = '__all__'


class ClientAccountSerializer(serializers.ModelSerializer):
    """Client Account Serializer"""
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = ClientAccount
        fields = '__all__'
