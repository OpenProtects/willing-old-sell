from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, EvaluationViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')

urlpatterns = [
    path('', include(router.urls)),
]
