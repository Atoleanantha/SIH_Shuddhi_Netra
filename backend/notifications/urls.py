from rest_framework.routers import DefaultRouter,path
from .views import NotificationViewSet, ComplaintViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'complaints', ComplaintViewSet, basename='complaint')
# router.register(r'detect/', CustomDetectionViewSet, basename='detect')
#  path('detect/', CustomDetectionView.as_view(), name='custom-detection'),

urlpatterns = router.urls + [
    path('complaints/<int:pk>/mark_actioned/', ComplaintViewSet.as_view({'patch': 'update'}), name='complaint-mark-actioned'),
    # path('detect', CustomDetectionViewSet.as_view(), name='custom-detection'),
]
