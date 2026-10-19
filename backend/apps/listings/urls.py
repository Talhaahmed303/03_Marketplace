from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ListingViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
]
