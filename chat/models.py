from django.db import models
from users.models import User


class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user1', verbose_name='用户1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user2', verbose_name='用户2')
    goods_id = models.IntegerField('关联物品ID', null=True, blank=True)
    goods_name = models.CharField('物品名称', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'chat_room'
        verbose_name = '聊天室'
        verbose_name_plural = '聊天室'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user1.username} <-> {self.user2.username}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name='聊天室')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    content = models.TextField('消息内容')
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('发送时间', auto_now_add=True)
    
    class Meta:
        db_table = 'chat_message'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}..."
