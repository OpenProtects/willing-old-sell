from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer, ReportHandleSerializer
from users.models import User, Notification
from credit.models import CreditRecord


class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            queryset = Report.objects.all()
        else:
            queryset = Report.objects.filter(reporter=user)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportSerializer
    
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
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            reported_user_id = serializer.validated_data['reported_user'].id
            
            if reported_user_id == request.user.id:
                return Response({
                    'code': 400,
                    'message': '不能举报自己'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            report = serializer.save(reporter=request.user, status='pending')
            
            return Response({
                'code': 200,
                'message': '举报提交成功',
                'data': ReportSerializer(report).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        report = self.get_object()
        
        if not request.user.is_admin:
            return Response({
                'code': 403,
                'message': '无权处理举报'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if report.status != 'pending':
            return Response({
                'code': 400,
                'message': '该举报已处理'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ReportHandleSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            report.status = data['status']
            report.result = data['result']
            report.handler = request.user
            report.handled_at = timezone.now()
            report.save()
            
            if data['status'] == 'resolved' and data.get('credit_deduction', 0) > 0:
                deduction = data['credit_deduction']
                reported_user = report.reported_user
                before_score = reported_user.credit_score
                after_score = max(0, before_score - deduction)
                reported_user.credit_score = after_score
                reported_user.save(update_fields=['credit_score'])
                
                CreditRecord.objects.create(
                    user=reported_user,
                    change_type='violation',
                    change_score=-deduction,
                    before_score=before_score,
                    after_score=after_score,
                    reason=f'违规被举报：{report.get_report_type_display()}',
                    related_report_id=report.id,
                    operator=request.user
                )
            
            Notification.objects.create(
                user=report.reporter,
                title='举报处理结果',
                content=f'您举报的用户"{report.reported_user.username}"的处理结果：{report.get_status_display()}。{report.result}',
                notification_type='report',
                related_id=report.id
            )
            
            if data['status'] == 'resolved':
                Notification.objects.create(
                    user=report.reported_user,
                    title='违规处理通知',
                    content=f'您因"{report.get_report_type_display()}"被举报，经核实违规成立。处理结果：{report.result}',
                    notification_type='report',
                    related_id=report.id
                )
            
            return Response({
                'code': 200,
                'message': '处理成功',
                'data': ReportSerializer(report).data
            })
        
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        queryset = Report.objects.filter(reporter=request.user).order_by('-created_at')
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
    
    @action(detail=False, methods=['get'])
    def reported_me(self, request):
        queryset = Report.objects.filter(reported_user=request.user).order_by('-created_at')
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
