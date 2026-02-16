from django.contrib import admin
from .models import Category, Goods


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'goods_count', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
    
    def goods_count(self, obj):
        return obj.goods.count()
    goods_count.short_description = '物品数量'


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'seller', 'category', 'price', 'condition', 
                    'status', 'view_count', 'is_traded', 'created_at']
    list_filter = ['status', 'condition', 'category', 'is_traded']
    search_fields = ['name', 'description', 'seller__username']
    raw_id_fields = ['seller', 'category']
    ordering = ['-created_at']
