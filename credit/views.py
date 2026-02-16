from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import CreditRecord
from .serializers import CreditRecordSerializer
from users.models import User


class CreditRecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CreditRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            queryset = CreditRecord.objects.all()
            user_id = self.request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = CreditRecord.objects.filter(user=user)
        
        change_type = self.request.query_params.get('change_type')
        if change_type:
            queryset = queryset.filter(change_type=change_type)
        
        return queryset.order_by('-created_at')
    
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
    
    @action(detail=False, methods=['post'])
    def adjust(self, request):
        if not request.user.is_admin:
            return Response({
                'code': 403,
                'message': '无权操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        change_score = request.data.get('change_score')
        reason = request.data.get('reason', '')
        
        if not user_id or change_score is None:
            return Response({
                'code': 400,
                'message': '缺少必要参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'code': 400,
                'message': '用户不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        before_score = target_user.credit_score
        after_score = max(0, min(200, before_score + change_score))
        target_user.credit_score = after_score
        target_user.save(update_fields=['credit_score'])
        
        record = CreditRecord.objects.create(
            user=target_user,
            change_type='admin_adjust',
            change_score=change_score,
            before_score=before_score,
            after_score=after_score,
            reason=reason,
            operator=request.user
        )
        
        return Response({
            'code': 200,
            'message': '调整成功',
            'data': CreditRecordSerializer(record).data
        })
    
    @action(detail=False, methods=['get'])
    def user_credit(self, request):
        user_id = request.query_params.get('user_id')
        if user_id and request.user.is_admin:
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'code': 400,
                    'message': '用户不存在'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_user = request.user
        
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'user_id': target_user.id,
                'username': target_user.username,
                'credit_score': target_user.credit_score
            }
        })
