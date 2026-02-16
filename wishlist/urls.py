from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet, MatchResultViewSet

router = DefaultRouter()
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'match-results', MatchResultViewSet, basename='match-result')

urlpatterns = [
    path('', include(router.urls)),
]
