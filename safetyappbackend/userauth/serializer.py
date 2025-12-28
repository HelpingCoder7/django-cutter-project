from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers

from .models import user_collection


class SignupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(min_length=10, max_length=10)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_phone_number(self, value):
        if not value.isdigit():
            message = "Phone number must contain only digits."
            raise serializers.ValidationError(
                message,
            )

        if cache.get(f"user:{value}:data") or user_collection.find_one(
            {"phone_number": int(value)},
        ):
            message = "Phone number is already registered."
            raise serializers.ValidationError(
                message,
            )

        return value

    def create(self, validated_data):
        user_data = {
            "phone_number": int(validated_data["phone_number"]),
            "password": make_password(validated_data["password"]),
            "created_at": timezone.now(),
            "is_active": True,
        }
        result = user_collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return user_data


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(min_length=10, max_length=10)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_phone_number(self, value):
        if not value.isdigit():
            message = "Phone number must contain only digits."
            raise serializers.ValidationError(
                message,
            )
        try:
            return int(value)
        except ValueError:
            message = "Invalid phone number"
            raise serializers.ValidationError(message) from None

    def validate(self, data):
        phone_number = data.get("phone_number")
        password = data.get("password")

        if not phone_number or not password:
            message = "Phone number and password are required."
            raise serializers.ValidationError(
                message,
            )

        cache_key_password = f"user:{phone_number}:password"
        cache_key_user = f"user:{phone_number}:data"

        cached_password = cache.get(cache_key_password)
        user = None

        # searciing in chache
        if cached_password and check_password(password, cached_password):
            user = cache.get(cache_key_user)

        # searching in db
        if not user:
            user = user_collection.find_one({"phone_number": phone_number})

            if not user:
                message = "User not found."
                raise serializers.ValidationError(
                    message,
                )

            if not check_password(password, user.get("password", "")):
                message = "Incorrect password."
                raise serializers.ValidationError(message)

            # storing in cache
            cache.set(cache_key_password, user["password"])
            cache.set(cache_key_user, user)

        data["user"] = user
        return data
