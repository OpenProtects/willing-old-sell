from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditRecordViewSet

router = DefaultRouter()
router.register(r'records', CreditRecordViewSet, basename='credit-record')

urlpatterns = [
    path('', include(router.urls)),
]
