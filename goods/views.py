from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Category, Goods
from .serializers import (
    CategorySerializer, GoodsListSerializer, GoodsDetailSerializer,
    GoodsCreateSerializer, GoodsUpdateSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })


class GoodsViewSet(viewsets.ModelViewSet):
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Goods.objects.select_related('seller', 'category').all()
        
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | Q(description__icontains=keyword)
            )
        
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        status_filter = self.request.query_params.get('status', 'on_sale')
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        seller_id = self.request.query_params.get('seller_id')
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GoodsCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GoodsUpdateSerializer
        elif self.action == 'retrieve':
            return GoodsDetailSerializer
        return GoodsListSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data,
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        goods = self.get_object()
        goods.view_count += 1
        goods.save(update_fields=['view_count'])
        serializer = self.get_serializer(goods)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            goods = serializer.save(seller=request.user)
            return Response({
                'code': 200,
                'message': '发布成功',
                'data': GoodsDetailSerializer(goods).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '发布失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        goods = self.get_object()
        if goods.seller != request.user:
            return Response({
                'code': 403,
                'message': '无权修改他人物品'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(goods, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': GoodsDetailSerializer(goods).data
            })
        return Response({
            'code': 400,
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        goods = self.get_object()
        if goods.seller != request.user:
            return Response({
                'code': 403,
                'message': '无权删除他人物品'
            }, status=status.HTTP_403_FORBIDDEN)
        
        goods.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        })
    
    @action(detail=True, methods=['post'])
    def off_shelf(self, request, pk=None):
        goods = self.get_object()
        if goods.seller != request.user:
            return Response({
                'code': 403,
                'message': '无权操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        goods.status = 'off_sale'
        goods.save(update_fields=['status'])
        return Response({
            'code': 200,
            'message': '下架成功'
        })
    
    @action(detail=True, methods=['post'])
    def on_shelf(self, request, pk=None):
        goods = self.get_object()
        if goods.seller != request.user:
            return Response({
                'code': 403,
                'message': '无权操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if goods.is_traded:
            return Response({
                'code': 400,
                'message': '该物品已交易，无法上架'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        goods.status = 'on_sale'
        goods.save(update_fields=['status'])
        return Response({
            'code': 200,
            'message': '上架成功'
        })
    
    @action(detail=False, methods=['get'])
    def my_goods(self, request):
        queryset = Goods.objects.filter(seller=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = GoodsListSerializer(page, many=True)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data,
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            })
        
        serializer = GoodsListSerializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import os
    import time
    
    file = request.FILES.get('file')
    if not file:
        return Response({
            'code': 400,
            'message': '请上传图片'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return Response({
            'code': 400,
            'message': '仅支持jpg、png、gif、webp格式图片'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if file.size > 5 * 1024 * 1024:
        return Response({
            'code': 400,
            'message': '图片大小不能超过5MB'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    ext = os.path.splitext(file.name)[1]
    filename = f"goods/{int(time.time())}_{request.user.id}{ext}"
    
    path = default_storage.save(filename, ContentFile(file.read()))
    url = f"/media/{path}"
    
    return Response({
        'code': 200,
        'message': '上传成功',
        'data': {'url': url}
    })
