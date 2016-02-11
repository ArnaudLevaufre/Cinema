from django.core.management.base import BaseCommand
from application.models import MovieDirectory


class Command(BaseCommand):
    help = "List all movie directories"

    def handle(self, *args, **options):
        movies_dirs = list(MovieDirectory.objects.all())
        if not movies_dirs:
            print("There is no movie directory")

        for directory in movies_dirs:
            print(directory.path)
