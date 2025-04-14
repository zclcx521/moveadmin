from rest_framework import serializers
from .models import Category, Drama

class DramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drama
        fields = ['id', 'title', 'cover', 'description', 'director', 'release_date', 
                 'total_episodes', 'status']

class CategoryWithDramasSerializer(serializers.ModelSerializer):
    dramas = DramaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'order', 'dramas']