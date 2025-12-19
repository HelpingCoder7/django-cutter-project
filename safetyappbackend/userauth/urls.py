from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AUTHVIEWSET

router = DefaultRouter()
router.register(r"auth", AUTHVIEWSET, basename="sign_up_view")
router.register(r"login", AUTHVIEWSET, basename="provide_otp")

app_name = "userauth"

urlpatterns = [
    path("api/", include(router.urls)),
]
