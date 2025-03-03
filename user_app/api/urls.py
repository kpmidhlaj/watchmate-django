from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path

from user_app.views import registration_view, logout_view
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from .views import UserCreateView
app_name = "user_app"

urlpatterns = [
    # path('register/', UserCreateView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('register/', registration_view, name='register'),
    path('logout/', logout_view, name='logout'),
    # path('logout/', obtain_auth_token, name='logout'),
    # path('register/', registration_view, name='register'),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
