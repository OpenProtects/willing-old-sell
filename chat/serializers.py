from rest_framework import serializers
from .models import ChatRoom, ChatMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    other_user_id = serializers.SerializerMethodField()
    other_user_name = serializers.SerializerMethodField()
    other_user_avatar = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'other_user_id', 'other_user_name', 'other_user_avatar',
                  'goods_id', 'goods_name', 'last_message', 'unread_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_other_user_id(self, obj):
        request_user = self.context['request'].user
        return obj.user2.id if obj.user1 == request_user else obj.user1.id
    
    def get_other_user_name(self, obj):
        request_user = self.context['request'].user
        return obj.user2.username if obj.user1 == request_user else obj.user1.username
    
    def get_other_user_avatar(self, obj):
        request_user = self.context['request'].user
        other_user = obj.user2 if obj.user1 == request_user else obj.user1
        return other_user.avatar.url if other_user.avatar else None
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content,
                'sender_id': last_msg.sender.id,
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request_user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=request_user).count()


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'sender_name', 'sender_avatar', 
                  'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']
    
    def get_sender_avatar(self, obj):
        return obj.sender.avatar.url if obj.sender.avatar else None


class SendMessageSerializer(serializers.Serializer):
    room_id = serializers.IntegerField(required=False)
    receiver_id = serializers.IntegerField()
    content = serializers.CharField(max_length=1000)
    goods_id = serializers.IntegerField(required=False, allow_null=True)
    goods_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
