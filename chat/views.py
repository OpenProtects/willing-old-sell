from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer, SendMessageSerializer
from users.models import User


class ChatRoomViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        ).order_by('-updated_at')
    
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
        room = self.get_object()
        if room.user1 != request.user and room.user2 != request.user:
            return Response({
                'code': 403,
                'message': '无权查看该聊天室'
            }, status=status.HTTP_403_FORBIDDEN)
        
        room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        
        messages = room.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'room': ChatRoomSerializer(room, context={'request': request}).data,
                'messages': serializer.data
            }
        })
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        serializer = SendMessageSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            receiver_id = data['receiver_id']
            content = data['content']
            goods_id = data.get('goods_id')
            goods_name = data.get('goods_name', '')
            
            try:
                receiver = User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                return Response({
                    'code': 400,
                    'message': '接收者不存在'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if receiver == request.user:
                return Response({
                    'code': 400,
                    'message': '不能给自己发送消息'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            room_id = data.get('room_id')
            if room_id:
                try:
                    room = ChatRoom.objects.get(id=room_id)
                    if room.user1 != request.user and room.user2 != request.user:
                        return Response({
                            'code': 403,
                            'message': '无权在该聊天室发送消息'
                        }, status=status.HTTP_403_FORBIDDEN)
                except ChatRoom.DoesNotExist:
                    return Response({
                        'code': 400,
                        'message': '聊天室不存在'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                room = ChatRoom.objects.filter(
                    Q(user1=request.user, user2=receiver) |
                    Q(user1=receiver, user2=request.user)
                ).first()
                
                if not room:
                    room = ChatRoom.objects.create(
                        user1=request.user,
                        user2=receiver,
                        goods_id=goods_id,
                        goods_name=goods_name
                    )
            
            message = ChatMessage.objects.create(
                room=room,
                sender=request.user,
                content=content
            )
            
            room.updated_at = timezone.now()
            room.save(update_fields=['updated_at'])
            
            return Response({
                'code': 200,
                'message': '发送成功',
                'data': ChatMessageSerializer(message).data
            })
        
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def get_or_create_room(self, request):
        receiver_id = request.query_params.get('receiver_id')
        goods_id = request.query_params.get('goods_id')
        goods_name = request.query_params.get('goods_name', '')
        
        if not receiver_id:
            return Response({
                'code': 400,
                'message': '缺少receiver_id参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({
                'code': 400,
                'message': '用户不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        room = ChatRoom.objects.filter(
            Q(user1=request.user, user2=receiver) |
            Q(user1=receiver, user2=request.user)
        ).first()
        
        if not room:
            room = ChatRoom.objects.create(
                user1=request.user,
                user2=receiver,
                goods_id=goods_id,
                goods_name=goods_name
            )
        
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': ChatRoomSerializer(room, context={'request': request}).data
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = ChatMessage.objects.filter(
            room__in=self.get_queryset(),
            is_read=False
        ).exclude(sender=request.user).count()
        
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {'count': count}
        })
