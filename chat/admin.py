from django.contrib import admin
from .models import ChatRoom, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'user1', 'user2', 'goods_id', 'goods_name', 'created_at', 'updated_at']
    search_fields = ['user1__username', 'user2__username', 'goods_name']
    raw_id_fields = ['user1', 'user2']
    ordering = ['-updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['content', 'sender__username']
    raw_id_fields = ['room', 'sender']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '消息内容'
