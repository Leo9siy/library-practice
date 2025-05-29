from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from User import views

urlpatterns = [
    path("register/", views.CreateUserView.as_view(), name="register"),
    path("me/", views.MeView.as_view(), name="me"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

app_name = "User"
