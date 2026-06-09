import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'email', 'username', 'password']

    def validate_email(self, value):
        if not re.match(r'^[a-z0-9]+\.admin@astraems\.com$', value):
            raise serializers.ValidationError(
                "Admin email must be: yourname.admin@astraems.com"
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            role='admin', is_staff=True, is_superuser=True,
            **validated_data
        )


class HRRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'email', 'username', 'password']

    def validate_email(self, value):
        if not re.match(r'^[a-z0-9]+\.hr@astraems\.com$', value):
            raise serializers.ValidationError(
                "HR email must be: yourname.hr@astraems.com"
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(role='hr', **validated_data)


class ManagerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'email', 'username', 'password']

    def validate_email(self, value):
        if not re.match(r'^[a-z0-9]+\.manager@astraems\.com$', value):
            raise serializers.ValidationError(
                "Manager email must be: yourname.manager@astraems.com"
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(role='manager', **validated_data)


class EmployeeSignupSerializer(serializers.ModelSerializer):
    """Public-facing signup. Account starts as PENDING until a manager approves."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'email', 'username', 'password']

    def create(self, validated_data):
        # is_active=False + status=pending set automatically in User.save()
        return User.objects.create_user(role='employee', **validated_data)


class ApproveEmployeeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    action  = serializers.ChoiceField(choices=['approve', 'reject'])


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            'id', 'email', 'username', 'role', 'status',
            'is_active', 'approved_by', 'approved_at', 'created_at',
        ]
        read_only_fields = ['id', 'role', 'status', 'approved_by', 'approved_at', 'created_at']