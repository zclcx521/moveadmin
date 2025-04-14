from django.core.management.base import BaseCommand
from drama.models import Category

class Command(BaseCommand):
    help = '初始化短剧类别数据'

    def handle(self, *args, **options):
        categories = [
            {'name': '古装', 'order': 1},
            {'name': '重生', 'order': 2},
            {'name': '恋爱', 'order': 3},
            {'name': '职场', 'order': 4},
            {'name': '复仇', 'order': 5},
            {'name': '都市', 'order': 6},
            {'name': '奇幻', 'order': 7},
        ]

        for category_data in categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'order': category_data['order']}
            )

        self.stdout.write(self.style.SUCCESS('成功初始化短剧类别数据'))