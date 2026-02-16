from rest_framework import serializers
from .models import Wishlist, MatchResult


class WishlistSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    match_status_display = serializers.CharField(source='get_match_status_display', read_only=True)
    match_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = ['id', 'name', 'category', 'category_name', 'min_price', 'max_price',
                  'description', 'keywords', 'match_status', 'match_status_display',
                  'match_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'keywords', 'match_status', 'created_at', 'updated_at']
    
    def get_match_count(self, obj):
        return obj.match_results.count()


class WishlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['name', 'category', 'min_price', 'max_price', 'description']


class WishlistUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['name', 'category', 'min_price', 'max_price', 'description']


class MatchResultSerializer(serializers.ModelSerializer):
    goods_images = serializers.SerializerMethodField()
    goods_condition = serializers.SerializerMethodField()
    goods_seller_id = serializers.SerializerMethodField()
    goods_seller_name = serializers.SerializerMethodField()
    goods_seller_credit = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchResult
        fields = ['id', 'wishlist', 'goods_id', 'goods_name', 'goods_price',
                  'goods_images', 'goods_condition', 'goods_seller_id',
                  'goods_seller_name', 'goods_seller_credit', 'similarity_score',
                  'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_goods_images(self, obj):
        from goods.models import Goods
        try:
            goods = Goods.objects.get(id=obj.goods_id)
            return goods.images
        except Goods.DoesNotExist:
            return []
    
    def get_goods_condition(self, obj):
        from goods.models import Goods
        try:
            goods = Goods.objects.get(id=obj.goods_id)
            return goods.get_condition_display()
        except Goods.DoesNotExist:
            return ''
    
    def get_goods_seller_id(self, obj):
        from goods.models import Goods
        try:
            goods = Goods.objects.get(id=obj.goods_id)
            return goods.seller.id
        except Goods.DoesNotExist:
            return None
    
    def get_goods_seller_name(self, obj):
        from goods.models import Goods
        try:
            goods = Goods.objects.get(id=obj.goods_id)
            return goods.seller.username
        except Goods.DoesNotExist:
            return ''
    
    def get_goods_seller_credit(self, obj):
        from goods.models import Goods
        try:
            goods = Goods.objects.get(id=obj.goods_id)
            return goods.seller.credit_score
        except Goods.DoesNotExist:
            return 0
