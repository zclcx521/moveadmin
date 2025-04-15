from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """短剧类别表"""
    name = models.CharField(_('类别名称'), max_length=50)
    order = models.IntegerField(_('排序'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('类别')
        verbose_name_plural = _('类别')
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

class Drama(models.Model):
    """短剧信息表"""
    title = models.CharField(_('标题'), max_length=100)
    cover = models.ImageField(_('封面'), upload_to='drama/covers/')
    description = models.TextField(_('简介'))
    director = models.CharField(_('导演'), max_length=50)
    release_date = models.DateField(_('上线日期'))
    total_episodes = models.IntegerField(_('总集数'))
    categories = models.ManyToManyField(Category, related_name='dramas', verbose_name=_('类别'))
    play_count = models.IntegerField(_('播放次数'), default=0)
    like_count = models.IntegerField(_('点赞次数'), default=0)
    share_count = models.IntegerField(_('转发次数'), default=0)
    status = models.CharField(_('状态'), max_length=20, choices=[
        ('draft', '草稿'),
        ('published', '已发布'),
        ('offline', '已下线')
    ], default='draft')
    recommendation_order = models.IntegerField(_('推荐顺序'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('短剧')
        verbose_name_plural = _('短剧')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Episode(models.Model):
    """剧集信息表"""
    drama = models.ForeignKey(Drama, on_delete=models.CASCADE, related_name='episodes', verbose_name=_('所属短剧'))
    title = models.CharField(_('标题'), max_length=100)
    episode_number = models.IntegerField(_('集数'))
    video_url = models.URLField(_('视频链接'))
    duration = models.IntegerField(_('时长'), help_text='单位：秒')
    thumbnail = models.ImageField(_('缩略图'), upload_to='drama/thumbnails/')
    views = models.IntegerField(_('播放量'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('剧集')
        verbose_name_plural = _('剧集')
        ordering = ['episode_number']
        unique_together = ['drama', 'episode_number']

    def __str__(self):
        return f'{self.drama.title} - 第{self.episode_number}集'

class Actor(models.Model):
    """演员信息表"""
    name = models.CharField(_('姓名'), max_length=50)
    avatar = models.ImageField(_('头像'), upload_to='drama/actors/')
    biography = models.TextField(_('简介'))
    dramas = models.ManyToManyField(Drama, through='DramaActor', related_name='actors', verbose_name=_('参演短剧'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('演员')
        verbose_name_plural = _('演员')
        ordering = ['name']

    def __str__(self):
        return self.name

class DramaActor(models.Model):
    """短剧演员关联表"""
    drama = models.ForeignKey(Drama, on_delete=models.CASCADE, verbose_name=_('短剧'))
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, verbose_name=_('演员'))
    role_name = models.CharField(_('角色名'), max_length=50)
    is_protagonist = models.BooleanField(_('是否主角'), default=False)

    class Meta:
        verbose_name = _('短剧演员')
        verbose_name_plural = _('短剧演员')
        unique_together = ['drama', 'actor']

    def __str__(self):
        return f'{self.drama.title} - {self.actor.name} ({self.role_name})'

class UserInteraction(models.Model):
    """用户互动信息表"""
    drama = models.ForeignKey(Drama, on_delete=models.CASCADE, related_name='interactions', verbose_name=_('短剧'))
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='interactions', verbose_name=_('剧集'))
    user_id = models.CharField(_('用户ID'), max_length=50)
    interaction_type = models.CharField(_('互动类型'), max_length=20, choices=[
        ('view', '观看'),
        ('like', '点赞'),
        ('comment', '评论'),
        ('share', '分享')
    ])
    content = models.TextField(_('内容'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('用户互动')
        verbose_name_plural = _('用户互动')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} - {self.interaction_type} - {self.drama.title}'