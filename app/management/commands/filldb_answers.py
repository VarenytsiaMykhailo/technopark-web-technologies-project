import random
from random import randrange

from django.core.management.base import BaseCommand, CommandError

from app.models import Answer, Question, User


class Command(BaseCommand):
    help = 'Заполнение БД: Answer'

    def add_arguments(self, parser):
        parser.add_argument('max_count', type=int)  # Max answers for every question

    def handle(self, *args, **options):
        max_count = int(options['max_count'])
        if max_count <= 0:
            raise CommandError('Параметр max_count должен быть больше 0.')
        users = User.objects.all()
        max_count = min(int(options['max_count']), len(users)) + 1
        for question in Question.objects.all():
            answers_count = randrange(0, max_count)
            for i in random.sample(range(len(users)), answers_count):
                answer = Answer.objects.create(question=question, author=users[i],
                                               text='This is the answer to the question!')
                answer.author.answer_added(question)
            question.save()
        print('filldb_answers: OK')