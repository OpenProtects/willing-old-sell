from django.contrib import admin
from .models import Wishlist, MatchResult


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'category', 'match_status', 'created_at']
    list_filter = ['match_status', 'category']
    search_fields = ['name', 'description', 'user__username']
    raw_id_fields = ['user', 'category']
    ordering = ['-created_at']


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'wishlist', 'goods_id', 'goods_name', 'goods_price', 
                    'similarity_score', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['goods_name', 'wishlist__name']
    raw_id_fields = ['wishlist']
    ordering = ['-similarity_score']
