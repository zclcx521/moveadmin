from rest_framework import serializers
from .models import Category, Drama, Actor, Episode

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name', 'avatar']

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ['id', 'title', 'episode_number', 'thumbnail', 'duration', 'views', 'video_url']

class DramaSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)
    first_episode_url = serializers.SerializerMethodField()
    actors = ActorSerializer(many=True, read_only=True)
    episodes_count = serializers.SerializerMethodField()
    first_episode_url = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    def get_first_episode_url(self, obj):
        if obj.episodes.exists():
            first_episode = obj.episodes.first()
            request = self.context.get('request')
            if request and first_episode.video_url:
                return request.build_absolute_uri(first_episode.video_url.url)
        return None

    def get_cover(self, obj):
        if not obj.cover:
            return None
        request = self.context.get('request')
        from django.conf import settings
        import logging
        logger = logging.getLogger(__name__)
        
        if request:
            url = request.build_absolute_uri(obj.cover.url)
            logger.debug(f'通过request生成封面URL: {url}')
        else:
            url = f'{settings.BASE_URL}{obj.cover.url}'
            logger.debug(f'通过BASE_URL生成封面URL: {url}')
            logger.debug(f'当前BASE_URL值: {settings.BASE_URL}')
        
        return url

    class Meta:
        model = Drama
        fields = ['id', 'title', 'cover', 'description', 'director', 'release_date',
                 'total_episodes', 'status', 'play_count', 'like_count', 'share_count',
                 'categories', 'actors', 'episodes_count']

    def get_episodes_count(self, obj):
        return obj.episodes.count()

class CategoryWithDramasSerializer(serializers.ModelSerializer):
    dramas = DramaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'dramas']