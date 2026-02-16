import jieba
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Wishlist, MatchResult
from .serializers import (
    WishlistSerializer, WishlistCreateSerializer, WishlistUpdateSerializer,
    MatchResultSerializer
)
from goods.models import Goods
from users.models import Notification


STOP_WORDS = set([
    '的', '了', '和', '是', '在', '有', '我', '他', '她', '它', '们',
    '这', '那', '就', '也', '都', '会', '能', '要', '可', '不', '没',
    '很', '还', '但', '又', '或', '与', '及', '等', '对', '把', '被',
    '让', '给', '向', '从', '到', '以', '为', '着', '过', '来', '去',
    '上', '下', '里', '外', '前', '后', '左', '右', '中', '大', '小',
    '多', '少', '高', '低', '长', '短', '好', '坏', '新', '旧', '想',
    '需要', '希望', '求购', '寻找', '想要', '希望', '能够', '可以',
])


def extract_keywords(text):
    if not text:
        return []
    
    words = jieba.cut(text)
    keywords = []
    for word in words:
        word = word.strip()
        if len(word) >= 2 and word not in STOP_WORDS:
            keywords.append(word)
    
    return list(set(keywords))


def calculate_similarity(wishlist, goods):
    score = 0
    
    wishlist_keywords = set(wishlist.keywords)
    goods_text = f"{goods.name} {goods.description}"
    goods_keywords = set(extract_keywords(goods_text))
    
    keyword_intersection = wishlist_keywords & goods_keywords
    if len(keyword_intersection) >= 1:
        keyword_score = len(keyword_intersection) / max(len(wishlist_keywords), 1)
        score += keyword_score * 0.5
    
    if wishlist.category and goods.category:
        if wishlist.category == goods.category:
            score += 0.2
    
    if wishlist.min_price and wishlist.max_price:
        if wishlist.min_price <= goods.price <= wishlist.max_price:
            score += 0.15
        elif goods.price < wishlist.min_price:
            score += 0.05
        elif goods.price > wishlist.max_price:
            price_diff = (goods.price - wishlist.max_price) / wishlist.max_price
            if price_diff <= 0.2:
                score += 0.05
    elif wishlist.min_price:
        if goods.price >= wishlist.min_price:
            score += 0.1
    elif wishlist.max_price:
        if goods.price <= wishlist.max_price:
            score += 0.1
    
    return min(score, 1.0)


def run_matching_for_wishlist(wishlist):
    goods_queryset = Goods.objects.filter(status='on_sale', is_traded=False)
    
    if wishlist.category:
        goods_queryset = goods_queryset.filter(category=wishlist.category)
    
    matched_goods = []
    for goods in goods_queryset:
        if goods.seller == wishlist.user:
            continue
        
        similarity = calculate_similarity(wishlist, goods)
        if similarity >= 0.1:
            matched_goods.append((goods, similarity))
    
    matched_goods.sort(key=lambda x: x[1], reverse=True)
    
    MatchResult.objects.filter(wishlist=wishlist).delete()
    
    match_results = []
    for goods, similarity in matched_goods[:5]:
        match_result = MatchResult.objects.create(
            wishlist=wishlist,
            goods_id=goods.id,
            goods_name=goods.name,
            goods_price=goods.price,
            similarity_score=similarity
        )
        match_results.append(match_result)
    
    if match_results:
        wishlist.match_status = 'matched'
        wishlist.save(update_fields=['match_status'])
        
        Notification.objects.create(
            user=wishlist.user,
            title='心愿单匹配成功',
            content=f'您的愿望"{wishlist.name}"已匹配到{len(match_results)}个相关物品，快去看看吧！',
            notification_type='match',
            related_id=wishlist.id
        )
    
    return match_results


class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WishlistCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WishlistUpdateSerializer
        return WishlistSerializer
    
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data,
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            wishlist = serializer.save(user=request.user)
            
            text = f"{wishlist.name} {wishlist.description or ''}"
            keywords = extract_keywords(text)
            wishlist.keywords = keywords
            wishlist.save(update_fields=['keywords'])
            
            match_results = run_matching_for_wishlist(wishlist)
            
            return Response({
                'code': 200,
                'message': '心愿单创建成功',
                'data': {
                    'wishlist': WishlistSerializer(wishlist).data,
                    'match_count': len(match_results)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            text = f"{wishlist.name} {wishlist.description or ''}"
            keywords = extract_keywords(text)
            wishlist.keywords = keywords
            wishlist.match_status = 'pending'
            wishlist.save(update_fields=['keywords', 'match_status'])
            
            match_results = run_matching_for_wishlist(wishlist)
            
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': {
                    'wishlist': WishlistSerializer(wishlist).data,
                    'match_count': len(match_results)
                }
            })
        
        return Response({
            'code': 400,
            'message': '参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        wishlist = self.get_object()
        wishlist.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        })
    
    @action(detail=True, methods=['post'])
    def rematch(self, request, pk=None):
        wishlist = self.get_object()
        match_results = run_matching_for_wishlist(wishlist)
        
        return Response({
            'code': 200,
            'message': '重新匹配成功',
            'data': {
                'match_count': len(match_results),
                'matches': MatchResultSerializer(match_results, many=True).data
            }
        })
    
    @action(detail=True, methods=['get'])
    def match_results(self, request, pk=None):
        wishlist = self.get_object()
        results = wishlist.match_results.all()
        serializer = MatchResultSerializer(results, many=True)
        
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })


class MatchResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MatchResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MatchResult.objects.filter(wishlist__user=self.request.user)
    
    def list(self, request):
        queryset = self.get_queryset()
        wishlist_id = request.query_params.get('wishlist_id')
        if wishlist_id:
            queryset = queryset.filter(wishlist_id=wishlist_id)
        
        queryset = queryset.order_by('-similarity_score')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data,
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        result = self.get_object()
        result.is_read = True
        result.save(update_fields=['is_read'])
        
        return Response({
            'code': 200,
            'message': '标记已读成功'
        })
