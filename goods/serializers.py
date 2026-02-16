from rest_framework import serializers
from .models import Category, Goods


class CategorySerializer(serializers.ModelSerializer):
    goods_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'goods_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_goods_count(self, obj):
        return obj.goods.filter(status='on_sale').count()


class GoodsListSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    seller_avatar = serializers.ImageField(source='seller.avatar', read_only=True)
    seller_credit = serializers.IntegerField(source='seller.credit_score', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Goods
        fields = ['id', 'name', 'category', 'category_name', 'description', 'price', 
                  'condition', 'condition_display', 'images', 'status', 'status_display',
                  'pickup_location', 'view_count', 'seller_name', 'seller_avatar', 
                  'seller_credit', 'created_at', 'is_traded']
        read_only_fields = ['id', 'view_count', 'created_at', 'seller']


class GoodsDetailSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    seller_avatar = serializers.ImageField(source='seller.avatar', read_only=True)
    seller_credit = serializers.IntegerField(source='seller.credit_score', read_only=True)
    seller_verified = serializers.BooleanField(source='seller.is_verified', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Goods
        fields = ['id', 'seller', 'seller_id', 'seller_name', 'seller_avatar', 
                  'seller_credit', 'seller_verified', 'name', 'category', 'category_name',
                  'description', 'price', 'condition', 'condition_display', 'images',
                  'status', 'status_display', 'pickup_location', 'view_count', 
                  'is_traded', 'created_at', 'updated_at']
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at', 'seller']


class GoodsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['name', 'category', 'description', 'price', 'condition', 
                  'images', 'pickup_location']
    
    def validate_images(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('图片必须是列表格式')
        if len(value) > 5:
            raise serializers.ValidationError('最多上传5张图片')
        return value


class GoodsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['name', 'category', 'description', 'price', 'condition', 
                  'images', 'pickup_location', 'status']
    
    def validate_images(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('图片必须是列表格式')
        if len(value) > 5:
            raise serializers.ValidationError('最多上传5张图片')
        return value
