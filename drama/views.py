from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
import logging

logger = logging.getLogger(__name__)
from django.db.models import Count, Q
from .models import Category, Drama, Episode
from .serializers import CategoryWithDramasSerializer, DramaSerializer, EpisodeSerializer

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

@api_view(['GET', 'POST'])
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
    if request.method == 'GET':
        try:
            dramas = Drama.objects.filter(
                status='published'
            ).prefetch_related(
                'categories',
                'actors',
                'episodes'
            ).annotate(
                popularity_score=Count('play_count') + Count('like_count') * 2 + Count('share_count') * 3
            ).order_by('-popularity_score')[:10]

            serializer = DramaSerializer(dramas, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in getting recommended_dramas: {str(e)}")
            return Response({'error': '获取推荐短剧失败'}, status=500)
    
    elif request.method == 'POST':
        try:
            drama_ids = request.data.get('drama_ids', [])
            if not drama_ids:
                return Response({'error': '未提供短剧ID'}, status=status.HTTP_400_BAD_REQUEST)
            
            dramas = Drama.objects.filter(id__in=drama_ids)
            if not dramas.exists():
                return Response({'error': '未找到指定的短剧'}, status=status.HTTP_404_NOT_FOUND)
            
            # 更新推荐顺序
            for index, drama_id in enumerate(drama_ids):
                drama = dramas.filter(id=drama_id).first()
                if drama:
                    drama.recommendation_order = index
                    drama.save()
            
            updated_dramas = Drama.objects.filter(id__in=drama_ids).order_by('recommendation_order')
            serializer = DramaSerializer(updated_dramas, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in setting recommended_dramas: {str(e)}")
            return Response({'error': '设置推荐短剧失败'}, status=500)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def category_dramas(request, category_name):
    logger.info(f"User {request.user} accessing dramas for category {category_name}")
    try:
        category = Category.objects.get(name=category_name)
        dramas = Drama.objects.filter(
            categories=category,
            status='published'
        ).prefetch_related(
            'categories',
            'actors',
            'episodes'
        ).order_by('-created_at')
        
        serializer = DramaSerializer(dramas, many=True, context={'request': request})
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response({'error': f'分类 {category_name} 不存在'}, status=404)
    except Exception as e:
        logger.error(f"Error in category_dramas: {str(e)}")
        return Response({'error': '获取分类短剧失败'}, status=500)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_drama_episodes(request):
    """
    获取指定短剧的剧集列表。
    
    该接口支持通过短剧ID或短剧名称来查询剧集信息。
    需要在请求头中添加 Authorization: Token your_token_here 进行身份验证。
    
    参数:
    request (HttpRequest): HTTP请求对象，包含查询参数。
    
    查询参数:
    id (str, 可选): 短剧的ID。
    name (str, 可选): 短剧的名称。
    
    返回:
    Response: 包含短剧标题、总集数和剧集列表的JSON响应。
    如果请求参数缺失或未找到指定短剧，返回相应的错误信息和状态码。
    如果发生其他异常，返回错误信息和500状态码。
    """
    logger.info(f"User {request.user} accessing drama episodes")
    try:
        # 从查询参数中获取短剧ID和名称
        drama_id = request.query_params.get('id')
        drama_name = request.query_params.get('name')

        # 检查是否提供了短剧ID或名称
        if not drama_id and not drama_name:
            return Response({'error': '请提供短剧ID或名称'}, status=status.HTTP_400_BAD_REQUEST)

        # 预加载剧集信息，提高查询性能
        drama_query = Drama.objects.prefetch_related('episodes')
        if drama_id:
            # 根据短剧ID查询短剧信息
            drama = drama_query.filter(id=drama_id).first()
        else:
            # 根据短剧名称查询短剧信息
            drama = drama_query.filter(title=drama_name).first()

        # 检查是否找到指定的短剧
        if not drama:
            return Response({'error': '未找到指定的短剧'}, status=status.HTTP_404_NOT_FOUND)

        # 查询指定短剧的所有剧集，并按集数排序
        episodes = Episode.objects.filter(drama=drama).order_by('episode_number')
        # 使用序列化器将剧集对象转换为JSON数据
        serializer = EpisodeSerializer(episodes, many=True)
        return Response({
            'drama_title': drama.title,  # 短剧标题
            'total_episodes': drama.total_episodes,  # 短剧总集数
            'episodes': serializer.data  # 剧集列表
        })
    except Exception as e:
        # 记录异常信息
        logger.error(f"Error in get_drama_episodes: {str(e)}")
        return Response({'error': '获取短剧剧集失败'}, status=500)