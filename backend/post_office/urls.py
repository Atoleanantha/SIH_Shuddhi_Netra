from rest_framework.routers import DefaultRouter
from post_office.views import PostOfficeViewSet
from django.urls import path

urlpatterns = [
    path('postoffice/', PostOfficeViewSet.as_view(), name='postoffice-list-create'),
]