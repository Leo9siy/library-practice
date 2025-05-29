from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from User.serializers import UserSerializer, UserDetailSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class MeView(RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
