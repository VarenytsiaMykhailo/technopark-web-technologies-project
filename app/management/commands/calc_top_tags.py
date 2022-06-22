from django.core.cache import cache
from django.core.management.base import BaseCommand

from app.models import QuestionTag


class Command(BaseCommand):
    help = 'Вычисления: лучшие теги'
    
    def add_arguments(self, parser):
        parser.add_argument('count', type=int)
    
    def handle(self, *args, **options):
        cache.set('top_tags', QuestionTag.objects.get_top(int(options['count'])))
        print('calc_top_tags: OK')
