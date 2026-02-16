from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'phone', 'email']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'real_name', 'avatar', 
                  'credit_score', 'is_verified', 'face_verified', 'school_id', 
                  'is_admin', 'date_joined', 'last_login']
        read_only_fields = ['id', 'credit_score', 'is_verified', 'face_verified', 'is_admin']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'real_name', 'avatar', 
                  'credit_score', 'is_verified', 'face_verified', 'school_id', 
                  'is_admin', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'credit_score', 'is_verified', 'face_verified', 'is_admin']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'email', 'avatar']
        extra_kwargs = {
            'phone': {'required': False},
            'email': {'required': False},
            'avatar': {'required': False},
        }


class RealNameVerifySerializer(serializers.Serializer):
    real_name = serializers.CharField(max_length=50)
    id_card = serializers.CharField(max_length=18)
    school_id = serializers.CharField(max_length=50, required=False, allow_blank=True)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'content', 'notification_type', 'related_id', 
                  'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    new_password_confirm = serializers.CharField(required=True, min_length=6)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '两次密码不一致'})
        return data
