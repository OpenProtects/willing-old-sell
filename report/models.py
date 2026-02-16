from django.db import models
from users.models import User


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('fake_info', '虚假物品信息'),
        ('malicious_chat', '恶意聊天'),
        ('fraud', '交易欺诈'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('rejected', '已驳回'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name='举报人')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_by', verbose_name='被举报人')
    report_type = models.CharField('举报类型', max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField('举报描述')
    evidence = models.JSONField('证据图片', default=list, blank=True)
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.TextField('处理结果', blank=True, null=True)
    handler = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_reports', verbose_name='处理人')
    handled_at = models.DateTimeField('处理时间', null=True, blank=True)
    created_at = models.DateTimeField('提交时间', auto_now_add=True)
    
    class Meta:
        db_table = 'report'
        verbose_name = '举报信息'
        verbose_name_plural = '举报信息'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reporter.username} 举报 {self.reported_user.username}"
