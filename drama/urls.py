from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, recommended_dramas, category_dramas, get_drama_episodes

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('recommended/', recommended_dramas, name='recommended-dramas'),
    path('category/<str:category_name>/', category_dramas, name='category-dramas'),
    path('episodes/', get_drama_episodes, name='drama-episodes'),
]

# Debug information - remove in production
from django.conf import settings
if settings.DEBUG:
    from rest_framework.authtoken.models import Token
    from django.contrib.auth.models import User
    try:
        # Ensure test user exists
        user = User.objects.filter(username='test').first()
        if user and not Token.objects.filter(user=user).exists():
            Token.objects.create(user=user)
    except Exception as e:
        print(f"Debug setup error: {e}")