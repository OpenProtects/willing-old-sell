from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import register_view, login_view, UserViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('', include(router.urls)),
]
