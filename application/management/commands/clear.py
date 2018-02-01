from itertools import chain
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from application.models import (MovieDirectory, Movie, MovieRequest, 
                NewMovieNotification, WatchlistItem, Subtitle)


class Command(BaseCommand):
    help = "Clear all Cinema data (for testing purpose)"

    def handle(self, *args, **options):
        all_models = [Movie, MovieDirectory, MovieRequest, 
                NewMovieNotification, Subtitle, WatchlistItem]

        for model in all_models:
            objects_to_delete = model.objects.all()
            print(f" Delete {len(objects_to_delete)} {model.__name__}")
            objects_to_delete.delete()

        for folder in ['films', 'posters', 'subtitles']:
            self.delete_folder(folder)


    def delete_folder(self, folder_name):
        print(f"Delete {folder_name} directory...")

        folder = os.path.join(settings.MEDIA_ROOT, folder_name)
        for the_file in os.listdir(folder):
            path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(path) and not the_file.startswith('.'):
                    os.unlink(path)
                    print(f"Delete file {path}")
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Delete directory {path}")
            except Exception as e:
                print(f"Exception while deleting {path}: {e}")
                break
