from django.core.management.base import BaseCommand
from application.models import MovieDirectory


class Command(BaseCommand):
    help = "Add a movie directory"

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        MovieDirectory.objects.create(path=options['path'])
