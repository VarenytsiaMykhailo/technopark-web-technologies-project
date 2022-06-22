from django.core.management.base import BaseCommand

from app.models import User


class Command(BaseCommand):
    help = 'Заполнение БД: User'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        for i in range(0, int(options['count'])):
            user = User.objects.create_user('User' + str(i), 'email' + str(i) + '@mail.ru', 'abracadabra')
            user.first_name = 'User name' + str(i) + ' first name'
            user.last_name = 'User last name' + str(i) + ' last name'
            user.save()
        print('filldb_users: OK')