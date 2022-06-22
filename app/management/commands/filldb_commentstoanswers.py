import random
from random import randrange

from django.core.management.base import BaseCommand, CommandError

from app.models import Answer, CommentToAnswer, User


class Command(BaseCommand):
    help = 'Заполнение БД: CommentToAnswer'

    def add_arguments(self, parser):
        parser.add_argument('max_count', type=int)

    def handle(self, *args, **options):
        max_count = int(options['max_count'])
        if max_count <= 0:
            raise CommandError('Параметр max_count должен быть больше 0.')
        users = User.objects.all()
        max_count = min(int(options['max_count']), len(users)) + 1
        for answer in Answer.objects.all():
            for i in random.sample(range(len(users)), randrange(0, max_count)):
                CommentToAnswer.objects.create(author=users[i], answer=answer,
                                               text='This is the comment to the answer.')
        print('filldb_commenttoanswer: OK')