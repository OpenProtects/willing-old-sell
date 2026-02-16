from django.db import models
from users.models import User
from goods.models import Category


class Wishlist(models.Model):
    MATCH_STATUS_CHOICES = [
        ('pending', '待匹配'),
        ('matched', '已匹配'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists', verbose_name='用户')
    name = models.CharField('物品名称', max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='wishlists', verbose_name='品类')
    min_price = models.DecimalField('最低价格', max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField('最高价格', max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField('需求描述', blank=True, null=True)
    keywords = models.JSONField('关键词列表', default=list, blank=True)
    match_status = models.CharField('匹配状态', max_length=20, choices=MATCH_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('提交时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'wishlist'
        verbose_name = '心愿单'
        verbose_name_plural = '心愿单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class MatchResult(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='match_results', verbose_name='心愿单')
    goods_id = models.IntegerField('物品ID')
    goods_name = models.CharField('物品名称', max_length=200)
    goods_price = models.DecimalField('物品价格', max_digits=10, decimal_places=2)
    similarity_score = models.FloatField('相似度分数', default=0)
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('匹配时间', auto_now_add=True)
    
    class Meta:
        db_table = 'match_result'
        verbose_name = '匹配结果'
        verbose_name_plural = '匹配结果'
        ordering = ['-similarity_score']
    
    def __str__(self):
        return f"{self.wishlist.name} - {self.goods_name}"
