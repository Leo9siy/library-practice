from rest_framework.routers import DefaultRouter

from Book.views import BookViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
urlpatterns = router.urls
