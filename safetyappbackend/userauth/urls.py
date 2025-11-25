
from . import views
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import Auth_viewset

router =DefaultRouter()
router.register(r'auth',Auth_viewset,basename='sign_up_view')
router.register(r'login',Auth_viewset,basename='provide_otp')

app_name ='userauth'

urlpatterns = [
    path("",views.home),
   
    

    path('api/',include(router.urls))

]
