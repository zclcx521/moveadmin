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
    actors = ActorSerializer(many=True, read_only=True)
    episodes_count = serializers.SerializerMethodField()

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