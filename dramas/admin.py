from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import Drama, Episode, Actor, DramaActor, UserInteraction

@admin.register(Drama)
class DramaAdmin(ImportExportModelAdmin):
    list_display = ['title', 'display_cover', 'director', 'release_date', 'total_episodes', 'status', 'created_at']
    list_filter = ['status', 'release_date']
    search_fields = ['title', 'director', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def display_cover(self, obj):
        if obj.cover:
            return format_html('<img src="{}" width="50" height="50" />', obj.cover.url)
        return ''
    display_cover.short_description = '封面'

@admin.register(Episode)
class EpisodeAdmin(ImportExportModelAdmin):
    list_display = ['drama', 'title', 'episode_number', 'display_thumbnail', 'duration', 'views', 'created_at']
    list_filter = ['drama', 'created_at']
    search_fields = ['title', 'drama__title']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    def display_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" />', obj.thumbnail.url)
        return ''
    display_thumbnail.short_description = '缩略图'

@admin.register(Actor)
class ActorAdmin(ImportExportModelAdmin):
    list_display = ['name', 'display_avatar', 'created_at']
    search_fields = ['name', 'biography']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['dramas']
    
    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
        return ''
    display_avatar.short_description = '头像'

@admin.register(DramaActor)
class DramaActorAdmin(ImportExportModelAdmin):
    list_display = ['drama', 'actor', 'role_name', 'is_protagonist']
    list_filter = ['drama', 'actor', 'is_protagonist']
    search_fields = ['drama__title', 'actor__name', 'role_name']

@admin.register(UserInteraction)
class UserInteractionAdmin(ImportExportModelAdmin):
    list_display = ['drama', 'episode', 'user_id', 'interaction_type', 'created_at']
    list_filter = ['interaction_type', 'created_at', 'drama']
    search_fields = ['user_id', 'content', 'drama__title']
    readonly_fields = ['created_at']