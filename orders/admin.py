from django.contrib import admin
from .models import Order, Evaluation


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_no', 'buyer', 'seller', 'goods', 'amount', 
                    'status', 'created_at', 'paid_at', 'completed_at']
    list_filter = ['status']
    search_fields = ['order_no', 'buyer__username', 'seller__username']
    raw_id_fields = ['buyer', 'seller', 'goods']
    ordering = ['-created_at']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'evaluator', 'evaluatee', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['order__order_no', 'evaluator__username', 'evaluatee__username']
    raw_id_fields = ['order', 'evaluator', 'evaluatee']
    ordering = ['-created_at']
