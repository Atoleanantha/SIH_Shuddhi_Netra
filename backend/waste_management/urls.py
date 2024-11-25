# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from waste_management.views import EwasteViewSet, PaperWasteViewSet, SelledPaperWasteViewSet,CleaningStaffViewSet,EventViewSet

# urls.py
from django.conf import settings
from django.conf.urls.static import static

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'ewaste', EwasteViewSet, basename='ewaste')
router.register(r'paperwaste', PaperWasteViewSet, basename='paperwaste')
router.register(r'selledpaperwaste', SelledPaperWasteViewSet, basename='selledpaperwaste')
router.register(r'cleaning-staff', CleaningStaffViewSet, basename='cleaning_staff')

'''*******  Event Endpoint ***********'''
router.register(r'event-management/event', EventViewSet, basename='events')


# The router will automatically create the URL patterns
urlpatterns = [
    path('', include(router.urls)),  # Include the automatically generated URLs
    # path('ewaste/', EwasteViewSet.as_view({'get': 'list', 'post': 'create'}), name='ewaste'),
    # path('paperwaste/', PaperWasteViewSet.as_view({'get': 'list', 'post': 'create'}), name='paperwaste'),
    # path('selledpaperwaste/', SelledPaperWasteViewSet.as_view({'get': 'list', 'post': 'create'}), name='selledpaperwaste'),
    # path('cleaning-staff/', CleaningStaffViewSet.as_view({'get': 'list', 'post': 'create'}), name='cleaning_staff'),
    # path('event-management/event/', EventViewSet.as_view({'get': 'list', 'post': 'create'}), name='events'),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
