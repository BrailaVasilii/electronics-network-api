from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NetworkNodeViewSet

# Create a router and register the viewset
router = DefaultRouter()
router.register(r'nodes', NetworkNodeViewSet, basename='networknode')

urlpatterns = [
    path('', include(router.urls)),
]