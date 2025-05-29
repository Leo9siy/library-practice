from rest_framework import viewsets

from Book import permissions
from Book.models import Book
from Book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (permissions.IsAdminReadOnly,)
