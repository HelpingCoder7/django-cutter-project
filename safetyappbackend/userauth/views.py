import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client

from .models import user_collection
from .serializer import SignupSerializer


# Create your views here.
@api_view(["get"])
def home(request):
    return Response("Women are safe")


class AUTHVIEWSET(viewsets.ViewSet):
    @action(detail=False, methods=["Post"])
    def signupview(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(
                type("UserObj", (), {"id": str(user["_id"])}),
            )
            return Response(
                {
                    "user": {"username": user["phone_number"]},
                    "access_token": str(refresh.access_token),
                },
            )
        return Response({"msg": "something went wrong"})

    @action(detail=False, methods=["Post"])
    def loginview(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if phone_number is None or password is None:
            return Response({"msg": phone_number})
        try:
            phone = int(phone_number)
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid phone number format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = user_collection.find_one({"phone_number": phone})
        if not user:
            return Response(
                {"error": f"User not found: {phone}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not check_password(password, user.get("password", "")):
            return Response({"error"})

        user_obj = type("UserObj", (), {"id": str(user["_id"])})()
        token = RefreshToken.for_user(user_obj)

        refresh = RefreshToken.for_user(user_obj)

        return Response(
            {
                "message": "Login successful",
                "user": {
                    "id": str(user["_id"]),
                    "phone_number": user["phone_number"],
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "token": str(token),
            },
            status=status.HTTP_200_OK,
        )

    def provide_otp(self, request):
        data = request.data

        otp = secrets.randbelow(1000000) + 1000

        if data.get("phone_number") is None:
            return Response({"msg": "required number"})

        try:
            account_sid = settings.ACCOUNT_SID
            auth_token = settings.AUTH_TOKEN

            client = Client(account_sid, auth_token)

            client.messages.create(
                from_="+12565489967",
                body=f"your otp is {otp} please do not share this otp to anyone",
                to=data.get("phone_number"),
            )
        except Exception(TimeoutError, ConnectionError, ValueError) as e:
            return Response({"msg": f"failed to send otp {e}"})

        return Response(
            {
                "msg": "otp sent",
            },
        )


@api_view(["post"])
def register_user(request):
    data = request.data

    records = {
        "phone_number": data.get["phone_number"],
        "password": data.get["passsword"],
    }
    find_user = user_collection.find({"phone_number": data.get["phone_number"]})
    if find_user is None:
        user_collection.insert_one(records)
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_208_ALREADY_REPORTED)


@api_view(["POST"])
def add_user(request):
    data = request.data

    phone_number = data.get("phone_number")

    password = data.get("password")

    if not phone_number or not password:
        return Response(
            {"error": "Missing required fields."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing_user = user_collection.find_one({"phone_number": phone_number})
    if existing_user:
        return Response(
            {"error": "User already exists."},
            status=status.HTTP_409_CONFLICT,
        )

    new_user = {
        "phone_number": phone_number,
        "password": password,
    }

    result = user_collection.insert_one(new_user)

    return Response(
        {
            "message": "User added successfully.",
            "user_id": str(result.inserted_id),
        },
        status=status.HTTP_201_CREATED,
    )
