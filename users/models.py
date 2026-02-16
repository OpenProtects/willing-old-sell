from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField('手机号', max_length=11, blank=True, null=True)
    real_name = models.CharField('真实姓名', max_length=50, blank=True, null=True)
    id_card = models.CharField('身份证号', max_length=100, blank=True, null=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    credit_score = models.IntegerField('诚信值', default=100)
    is_verified = models.BooleanField('实名认证状态', default=False)
    face_verified = models.BooleanField('人脸认证状态', default=False)
    school_id = models.CharField('学号/工号', max_length=50, blank=True, null=True)
    is_admin = models.BooleanField('是否管理员', default=False)
    
    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username


class Notification(models.Model):
    TYPE_CHOICES = [
        ('match', '心愿单匹配'),
        ('order', '订单通知'),
        ('evaluation', '评价通知'),
        ('report', '举报处理'),
        ('system', '系统通知'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='用户')
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    notification_type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES, default='system')
    related_id = models.IntegerField('关联ID', null=True, blank=True)
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'notification'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
