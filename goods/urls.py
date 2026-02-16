from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, GoodsViewSet, upload_image

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'goods', GoodsViewSet, basename='goods')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', upload_image, name='upload_image'),
]
