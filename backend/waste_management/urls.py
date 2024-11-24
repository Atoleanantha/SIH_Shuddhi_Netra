# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from waste_management.views import EwasteViewSet, PaperWasteViewSet, SelledPaperWasteViewSet,CleaningStaffViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'ewaste', EwasteViewSet, basename='ewaste')
router.register(r'paperwaste', PaperWasteViewSet, basename='paperwaste')
router.register(r'selledpaperwaste', SelledPaperWasteViewSet, basename='selledpaperwaste')
router.register(r'cleaning-staff', CleaningStaffViewSet, basename='cleaning_staff')

# The router will automatically create the URL patterns
urlpatterns = [
    path('', include(router.urls)),  # Include the automatically generated URLs
]
