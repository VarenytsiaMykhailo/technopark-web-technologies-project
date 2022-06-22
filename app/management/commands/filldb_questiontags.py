from django.core.management.base import BaseCommand, CommandError

from app.models import QuestionTag


class Command(BaseCommand):
    help = 'Заполнение БД: QuestionTag'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        count = int(options['count'])
        if count <= 0:
            raise CommandError('Параметр count должен быть больше 0.')
        for i in range(0, int(count)):
            QuestionTag.objects.create(name='Tag' + str(i), description='This it description of tag number ' + str(i))
        print('filldb_questiontags: OK')