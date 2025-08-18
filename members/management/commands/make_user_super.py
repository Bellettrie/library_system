from django.contrib.auth.models import User

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Make a user super'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str, help='User to make super')

    def handle(self, *args, **options):
        user = User.objects.get(username=options['user'])
        user.is_superuser = True
        user.is_staff = True
        user.save()
