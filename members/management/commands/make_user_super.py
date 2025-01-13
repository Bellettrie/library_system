from django.contrib.auth.models import Group, Permission, User

from django.core.management.base import BaseCommand

from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL


class Command(BaseCommand):
    help = 'Make a user super'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str, help='User to make super')

    def handle(self, *args, **options):
        user=User.objects.get(username=options['user'])
        user.is_superuser=True
        user.is_staff=True
        user.save()