from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Notification
from .serializers import (
    UserRegisterSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, UserUpdateSerializer, RealNameVerifySerializer,
    NotificationSerializer, ChangePasswordSerializer
)
import os
import time

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'code': 200,
            'message': '注册成功',
            'data': {
                'user': UserSerializer(user).data,
                'token': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_201_CREATED)
    return Response({
        'code': 400,
        'message': '注册失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user:
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            refresh = RefreshToken.for_user(user)
            return Response({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'user': UserSerializer(user).data,
                    'token': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }
            })
        return Response({
            'code': 401,
            'message': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
    return Response({
        'code': 400,
        'message': '参数错误',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return User.objects.all().order_by('-date_joined')
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserProfileSerializer
    
    def list(self, request):
        if request.user.is_admin:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = UserSerializer(page, many=True)
                return Response({
                    'code': 200,
                    'message': '获取成功',
                    'data': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link()
                })
            serializer = UserSerializer(queryset, many=True)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(request.user)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def verify_realname(self, request):
        serializer = RealNameVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            real_name = serializer.validated_data['real_name']
            id_card = serializer.validated_data['id_card']
            school_id = serializer.validated_data.get('school_id', '')
            
            import hashlib
            encrypted_id_card = hashlib.sha256(id_card.encode()).hexdigest()
            
            user.real_name = real_name
            user.id_card = encrypted_id_card
            user.school_id = school_id
            user.is_verified = True
            user.face_verified = True
            user.save()
            
            return Response({
                'code': 200,
                'message': '实名认证成功',
                'data': UserSerializer(user).data
            })
        return Response({
            'code': 400,
            'message': '认证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'code': 400,
                    'message': '原密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'code': 200,
                'message': '密码修改成功'
            })
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def credit_records(self, request):
        from credit.models import CreditRecord
        records = CreditRecord.objects.filter(user=request.user).order_by('-created_at')
        from credit.serializers import CreditRecordSerializer
        serializer = CreditRecordSerializer(records, many=True)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    
    def partial_update(self, request, pk=None):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': UserSerializer(user).data
            })
        return Response({
            'code': 400,
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
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
        
        if file.size > 2 * 1024 * 1024:
            return Response({
                'code': 400,
                'message': '图片大小不能超过2MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ext = os.path.splitext(file.name)[1]
        filename = f"avatars/{int(time.time())}_{request.user.id}{ext}"
        
        path = default_storage.save(filename, ContentFile(file.read()))
        url = f"/media/{path}"
        
        request.user.avatar = path
        request.user.save(update_fields=['avatar'])
        
        return Response({
            'code': 200,
            'message': '上传成功',
            'data': {'url': url}
        })


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def list(self, request):
        queryset = self.get_queryset()
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
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
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({
            'code': 200,
            'message': '标记已读成功'
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({
            'code': 200,
            'message': '全部标记已读成功'
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {'count': count}
        })
