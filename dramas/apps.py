from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DramasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dramas'
    verbose_name = _('短剧管理')