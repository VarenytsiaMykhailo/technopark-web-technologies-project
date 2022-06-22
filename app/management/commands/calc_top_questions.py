from django.core.cache import cache
from django.core.management.base import BaseCommand

from app.models import Question


class Command(BaseCommand):
    help = 'Вычисления: лучшие вопросы'
    
    def add_arguments(self, parser):
        parser.add_argument('min_rating', type=int)
    
    def handle(self, *args, **options):
        cache.set('top_questions', Question.objects.get_top(int(options['min_rating'])))
        print('calc_top_questions: OK')
