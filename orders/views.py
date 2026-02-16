from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
import uuid
from .models import Order, Evaluation
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    EvaluationSerializer, EvaluationCreateSerializer
)
from goods.models import Goods
from users.models import User
from credit.models import CreditRecord


def create_credit_record(user, change_type, change_score, reason, 
                         related_order_id=None, related_report_id=None, operator=None):
    before_score = user.credit_score
    after_score = max(0, min(200, before_score + change_score))
    user.credit_score = after_score
    user.save(update_fields=['credit_score'])
    
    CreditRecord.objects.create(
        user=user,
        change_type=change_type,
        change_score=change_score,
        before_score=before_score,
        after_score=after_score,
        reason=reason,
        related_order_id=related_order_id,
        related_report_id=related_report_id,
        operator=operator
    )
    return after_score


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Order.objects.select_related('buyer', 'seller', 'goods').all()
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        role = self.request.query_params.get('role')
        if role == 'buyer':
            queryset = queryset.filter(buyer=self.request.user)
        elif role == 'seller':
            queryset = queryset.filter(seller=self.request.user)
        else:
            queryset = queryset.filter(
                buyer=self.request.user
            ) | queryset.filter(seller=self.request.user)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
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
        order = self.get_object()
        if order.buyer != request.user and order.seller != request.user:
            return Response({
                'code': 403,
                'message': '无权查看该订单'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(order)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            goods_id = serializer.validated_data['goods_id']
            
            try:
                goods = Goods.objects.get(id=goods_id, status='on_sale', is_traded=False)
            except Goods.DoesNotExist:
                return Response({
                    'code': 400,
                    'message': '物品不存在或已下架'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if goods.seller == request.user:
                return Response({
                    'code': 400,
                    'message': '不能购买自己的物品'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not request.user.is_verified:
                return Response({
                    'code': 400,
                    'message': '请先完成实名认证'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            order_no = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
            
            order = Order.objects.create(
                order_no=order_no,
                buyer=request.user,
                seller=goods.seller,
                goods=goods,
                amount=goods.price
            )
            
            return Response({
                'code': 200,
                'message': '订单创建成功',
                'data': OrderDetailSerializer(order).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        
        if order.buyer != request.user:
            return Response({
                'code': 403,
                'message': '无权操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'pending':
            return Response({
                'code': 400,
                'message': '订单状态不正确'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save(update_fields=['status', 'paid_at'])
        
        return Response({
            'code': 200,
            'message': '支付成功（模拟支付）',
            'data': OrderDetailSerializer(order).data
        })
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        order = self.get_object()
        
        if order.buyer != request.user:
            return Response({
                'code': 403,
                'message': '无权操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if order.status != 'paid':
            return Response({
                'code': 400,
                'message': '订单状态不正确'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save(update_fields=['status', 'completed_at'])
            
            goods = order.goods
            goods.status = 'sold'
            goods.is_traded = True
            goods.save(update_fields=['status', 'is_traded'])
        
        return Response({
            'code': 200,
            'message': '确认收货成功',
            'data': OrderDetailSerializer(order).data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.buyer != request.user and order.seller != request.user:
            return Response({
                'code': 403,
                'message': '无权操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if order.status not in ['pending', 'paid']:
            return Response({
                'code': 400,
                'message': '订单状态不正确'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.save(update_fields=['status', 'cancelled_at'])
        
        return Response({
            'code': 200,
            'message': '订单已取消'
        })


class EvaluationViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Evaluation.objects.filter(evaluator=self.request.user).order_by('-created_at')
    
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
    
    def create(self, request):
        serializer = EvaluationCreateSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order'].id
            
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({
                    'code': 400,
                    'message': '订单不存在'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if order.status != 'completed':
                return Response({
                    'code': 400,
                    'message': '订单未完成，无法评价'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if order.buyer != request.user and order.seller != request.user:
                return Response({
                    'code': 403,
                    'message': '无权评价该订单'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if Evaluation.objects.filter(order=order, evaluator=request.user).exists():
                return Response({
                    'code': 400,
                    'message': '该订单已评价'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            evaluatee = order.seller if request.user == order.buyer else order.buyer
            rating = serializer.validated_data['rating']
            content = serializer.validated_data.get('content', '')
            
            evaluation = Evaluation.objects.create(
                order=order,
                evaluator=request.user,
                evaluatee=evaluatee,
                rating=rating,
                content=content
            )
            
            if rating == 'good':
                create_credit_record(
                    user=evaluatee,
                    change_type='evaluation_good',
                    change_score=1,
                    reason=f'收到好评（订单：{order.order_no}）',
                    related_order_id=order.id
                )
            elif rating == 'bad':
                create_credit_record(
                    user=evaluatee,
                    change_type='evaluation_bad',
                    change_score=-2,
                    reason=f'收到差评（订单：{order.order_no}）',
                    related_order_id=order.id
                )
            
            return Response({
                'code': 200,
                'message': '评价成功',
                'data': EvaluationSerializer(evaluation).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
