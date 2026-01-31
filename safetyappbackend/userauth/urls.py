from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AUTHVIEWSET
from .views import healthz

router = DefaultRouter()
router.register(r"auth", AUTHVIEWSET, basename="login_signup")
router.register(r"otp", AUTHVIEWSET, basename="provide_otp")

app_name = "userauth"

urlpatterns = [
    path("api/", include(router.urls)),
    path("healthz/", healthz, name="healthz"),
]
