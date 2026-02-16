from django.db import models
from users.models import User


class CreditRecord(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('evaluation_good', '好评加分'),
        ('evaluation_bad', '差评扣分'),
        ('violation', '违规扣分'),
        ('admin_adjust', '管理员调整'),
        ('system', '系统调整'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_records', verbose_name='用户')
    change_type = models.CharField('变更类型', max_length=20, choices=CHANGE_TYPE_CHOICES)
    change_score = models.IntegerField('变更分值')
    before_score = models.IntegerField('变更前分数')
    after_score = models.IntegerField('变更后分数')
    reason = models.CharField('变更原因', max_length=500)
    related_order_id = models.IntegerField('关联订单ID', null=True, blank=True)
    related_report_id = models.IntegerField('关联举报ID', null=True, blank=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operated_credit_records', verbose_name='操作人')
    created_at = models.DateTimeField('变更时间', auto_now_add=True)
    
    class Meta:
        db_table = 'credit_record'
        verbose_name = '诚信值记录'
        verbose_name_plural = '诚信值记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} {self.change_score:+d} ({self.change_type})"
