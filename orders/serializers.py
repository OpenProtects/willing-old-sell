from rest_framework import serializers
from .models import Order, Evaluation


class OrderListSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_image = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_no', 'buyer', 'buyer_name', 'seller', 'seller_name',
                  'goods', 'goods_name', 'goods_image', 'amount', 'status', 
                  'status_display', 'created_at', 'paid_at', 'completed_at']
        read_only_fields = ['id', 'order_no', 'created_at']
    
    def get_goods_image(self, obj):
        images = obj.goods.images
        if images and len(images) > 0:
            return images[0]
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    buyer_avatar = serializers.ImageField(source='buyer.avatar', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    seller_avatar = serializers.ImageField(source='seller.avatar', read_only=True)
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_description = serializers.CharField(source='goods.description', read_only=True)
    goods_images = serializers.JSONField(source='goods.images', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    evaluation = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_no', 'buyer', 'buyer_name', 'buyer_avatar',
                  'seller', 'seller_name', 'seller_avatar', 'goods', 'goods_name',
                  'goods_description', 'goods_images', 'amount', 'status', 
                  'status_display', 'created_at', 'paid_at', 'completed_at', 
                  'cancelled_at', 'evaluation']
        read_only_fields = ['id', 'order_no', 'created_at']
    
    def get_evaluation(self, obj):
        try:
            evaluation = obj.evaluation
            return EvaluationSerializer(evaluation).data
        except:
            return None


class OrderCreateSerializer(serializers.Serializer):
    goods_id = serializers.IntegerField()


class EvaluationSerializer(serializers.ModelSerializer):
    evaluator_name = serializers.CharField(source='evaluator.username', read_only=True)
    evaluatee_name = serializers.CharField(source='evaluatee.username', read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = ['id', 'order', 'evaluator', 'evaluator_name', 'evaluatee', 
                  'evaluatee_name', 'rating', 'rating_display', 'content', 'created_at']
        read_only_fields = ['id', 'evaluator', 'evaluatee', 'created_at']


class EvaluationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ['order', 'rating', 'content']
    
    def validate_rating(self, value):
        if value not in ['good', 'neutral', 'bad']:
            raise serializers.ValidationError('评价类型无效')
        return value
