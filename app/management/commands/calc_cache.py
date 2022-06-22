from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Вычисления'
    
    def handle(self, *args, **options):
        call_command('calc_top_tags', 10)
        call_command('calc_top_questions', 10)
        call_command('calc_top_users', 10)
        print('calc_cache: OK')
