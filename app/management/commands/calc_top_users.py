from django.core.cache import cache
from django.core.management.base import BaseCommand

from app.models import User


class Command(BaseCommand):
    help = 'Вычисления: лучшие пользователи'
    
    def add_arguments(self, parser):
        parser.add_argument('count', type=int)
    
    def handle(self, *args, **options):
        cache.set('top_users', User.objects.get_top(int(options['count'])))
        print('calc_top_users: OK')
