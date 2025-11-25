  # noqa: EXE002
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import serializers

from .models import user_collection


class SignupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10, min_length=10)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_phone_number(self, value):
        if not value.isdigit():
            msg = "Phone number must contain only digits."
            raise serializers.ValidationError(msg)
        # Check if user already exists
        if user_collection.find_one({"phone_number": value}):
            msg = "Phone number already registered."
            raise serializers.ValidationError(msg)
        return value

    def validate_password(self, value):
        if len(value) < 8:  # noqa: PLR2004
            msg = "Password must be at least 8 characters."
            raise serializers.ValidationError(msg)
        return value

    def create(self, validated_data):
        user_data = {
            "phone_number": validated_data["phone_number"],
            "password": make_password(validated_data["password"]),
            "created_at": timezone.now(),
            "is_active": True,
        }
        result = user_collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return user_data
