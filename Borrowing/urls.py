from rest_framework.routers import DefaultRouter

from Borrowing import views

router = DefaultRouter()
router.register("borrowings", views.BorrowingViewSet, basename="borrowing")

urlpatterns = router.urls

app_name = "Borrowing"
