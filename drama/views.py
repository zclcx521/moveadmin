from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import logging

logger = logging.getLogger(__name__)
from django.db.models import Count, Q
from .models import Category, Drama
from .serializers import CategoryWithDramasSerializer, DramaSerializer

class CategoryViewSet(ReadOnlyModelViewSet):
    """
    获取短剧类别及其包含的短剧列表
    需要在请求头中添加 Authorization: Token your_token_here
    """
    queryset = Category.objects.prefetch_related('dramas').all()
    serializer_class = CategoryWithDramasSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        logger.info(f"User {request.user} accessing categories list")
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"User {request.user} accessing category detail {kwargs.get('pk')}")
        return super().retrieve(request, *args, **kwargs)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def recommended_dramas(request):
    logger.info(f"User {request.user} accessing recommended dramas")
    """
    获取推荐的短剧列表
    推荐规则：
    1. 状态为已发布
    2. 按播放量、点赞数和分享数的综合评分排序
    3. 预加载相关数据以提高性能
    """
    dramas = Drama.objects.filter(
        status='published'
    ).prefetch_related(
        'categories',
        'actors',
        'episodes'
    ).annotate(
        popularity_score=Count('play_count') + Count('like_count') * 2 + Count('share_count') * 3
    ).order_by('-popularity_score')[:10]

    serializer = DramaSerializer(dramas, many=True)
    return Response(serializer.data)