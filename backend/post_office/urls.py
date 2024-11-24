from rest_framework.routers import DefaultRouter
from post_office.views import PostOfficeViewSet

router = DefaultRouter()
router.register(r'postoffice', PostOfficeViewSet, basename='postoffice')

urlpatterns = router.urls