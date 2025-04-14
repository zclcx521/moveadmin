from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from .models import Category
from .serializers import CategoryWithDramasSerializer

class CategoryViewSet(ReadOnlyModelViewSet):
    """
    获取短剧类别及其包含的短剧列表
    """
    queryset = Category.objects.prefetch_related('dramas').all()
    serializer_class = CategoryWithDramasSerializer
    permission_classes = [AllowAny]