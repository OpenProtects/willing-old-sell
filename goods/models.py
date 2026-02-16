from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField('品类名称', max_length=50, unique=True)
    description = models.TextField('品类描述', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'category'
        verbose_name = '物品品类'
        verbose_name_plural = '物品品类'
    
    def __str__(self):
        return self.name


class Goods(models.Model):
    STATUS_CHOICES = [
        ('on_sale', '上架中'),
        ('off_sale', '已下架'),
        ('sold', '已售出'),
    ]
    
    CONDITION_CHOICES = [
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goods', verbose_name='卖家')
    name = models.CharField('物品名称', max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='goods', verbose_name='品类')
    description = models.TextField('物品描述')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    condition = models.CharField('新旧程度', max_length=20, choices=CONDITION_CHOICES, default='good')
    images = models.JSONField('图片列表', default=list, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='on_sale')
    pickup_location = models.CharField('取货地点', max_length=200, blank=True, null=True)
    view_count = models.IntegerField('浏览次数', default=0)
    is_traded = models.BooleanField('是否已交易', default=False)
    created_at = models.DateTimeField('发布时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'goods'
        verbose_name = '闲置物品'
        verbose_name_plural = '闲置物品'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
