from django.core.management.base import BaseCommand
from application.models import MovieDirectory


class Command(BaseCommand):
    help = "Remove a movie directory"

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        for directory in MovieDirectory.objects.filter(path=options['path']):
            directory.delete()
