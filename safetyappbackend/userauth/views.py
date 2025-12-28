import secrets

from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client

from .serializer import LoginSerializer
from .serializer import SignupSerializer

# Create your views here.


class AUTHVIEWSET(viewsets.ViewSet):
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

    @action(detail=False, methods=["Post"])
    def signupview(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"msg": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        refresh = RefreshToken.for_user(
            type("UserObj", (), {"id": str(user["_id"])}),
        )
        return Response(
            {
                "user": {"username": user["phone_number"]},
                "access_token": str(refresh.access_token),
                "status": status.HTTP_201_CREATED,
            },
        )

    @action(detail=False, methods=["POST"])
    def loginview(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            message = "Login failed"
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.validated_data["user"]

        user_obj = type("UserObj", (), {"id": str(user["_id"])})()
        refresh = RefreshToken.for_user(user_obj)

        message = "Login successful"

        return Response(
            {
                "message": message,
                "user": {
                    "id": str(user["_id"]),
                    "phone_number": user["phone_number"],
                },
                "refresh": str(refresh),
                "access_token": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )
