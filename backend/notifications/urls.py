from rest_framework.routers import DefaultRouter,path
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
# router.register(r'detect/', CustomDetectionViewSet, basename='detect')
#  path('detect/', CustomDetectionView.as_view(), name='custom-detection'),

urlpatterns = router.urls + [
    # path('detect', CustomDetectionViewSet.as_view(), name='custom-detection'),
]
