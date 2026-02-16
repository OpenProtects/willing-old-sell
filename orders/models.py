from django.db import models
from users.models import User
from goods.models import Goods


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    order_no = models.CharField('订单号', max_length=50, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_orders', verbose_name='买家')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_orders', verbose_name='卖家')
    goods = models.OneToOneField(Goods, on_delete=models.CASCADE, related_name='order', verbose_name='物品')
    amount = models.DecimalField('订单金额', max_digits=10, decimal_places=2)
    status = models.CharField('订单状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    paid_at = models.DateTimeField('支付时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    cancelled_at = models.DateTimeField('取消时间', null=True, blank=True)
    
    class Meta:
        db_table = 'order'
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.order_no


class Evaluation(models.Model):
    RATING_CHOICES = [
        ('good', '好评'),
        ('neutral', '中评'),
        ('bad', '差评'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='evaluation', verbose_name='订单')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations', verbose_name='评价人')
    evaluatee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_evaluations', verbose_name='被评价人')
    rating = models.CharField('评价类型', max_length=20, choices=RATING_CHOICES)
    content = models.TextField('评价内容', blank=True, null=True)
    created_at = models.DateTimeField('评价时间', auto_now_add=True)
    
    class Meta:
        db_table = 'evaluation'
        verbose_name = '评价'
        verbose_name_plural = '评价'
    
    def __str__(self):
        return f"{self.evaluator.username} -> {self.evaluatee.username} ({self.rating})"
