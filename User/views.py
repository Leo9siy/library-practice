from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

import User
from User.serializers import UserSerializer, UserDetailSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class MeView(RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user
