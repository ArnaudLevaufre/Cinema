import os
import re
import json
import datetime
from urllib.request import urlopen
from urllib.parse import urlencode
from django.core.management.base import BaseCommand
from application.models import Movie
from django.conf import settings
from django.db.utils import IntegrityError

MOVIES_EXT = [
    '.mp4',
    '.mkv',
]

UPLOADERS = [
    'yify',
    'judas',
    'anoxmous_',
    'aac-rarbg',
    'bokutox',
    'deceit',
    'web-dl',
]


class API:
    def clean_name(self, name):
        name = name.lower()
        name = re.sub('1080p|720p', '', name)
        name = re.sub('bluray|brrip|brrip', '', name)
        name = re.sub('|'.join(UPLOADERS), '', name)
        name = re.sub('x264|H264|\+hi|aac|h.264', '', name, re.IGNORECASE)
        name = re.sub('5.1|7.1', '', name)
        name = re.sub('(19|20)[0-9]{2}', '', name)
        name = re.sub('extended|remastered', '', name)
        name = re.sub('\.', ' ', name)
        return name.strip()

    def search(self, name):
        name = self.clean_name(name)
        params = urlencode({'s': name, 'r': 'json'})
        url = 'http://www.omdbapi.com/?%s' % params
        with urlopen(url) as request:
            resp = json.loads(request.read().decode())
            if "Search" in resp:
                for res in resp['Search']:
                    try:
                        date = datetime.date(int(res['Year']), 1, 1)
                    except ValueError:
                        date = None
                    yield {
                        'title': res['Title'],
                        'date': date,
                        'imdbid': res['imdbID'],
                        'poster': res['Poster'] if res['Poster'] != "N/A" else None,
                    }


class Crawler:
    def __init__(self, api=API):
        self.api = api()
        self.movies = [m.path for m in Movie.objects.all()]

    def crawl(self, path):
        print("Updating database")
        for dirname, subdirs, files in os.walk(path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext not in MOVIES_EXT:
                    continue
                path = os.path.join(dirname, filename)
                self.handle_file(name, path)
                print(path)

    def handle_file(self, name, path):
        if path in self.movies:
            return
        match = self.api.search(name)
        try:
            for m in match:
                poster_name = self.save_poster(m['poster'])
                os.symlink(path, os.path.join(settings.MEDIA_ROOT, 'films', os.path.basename(path)))
                Movie.objects.create(
                    title=m['title'],
                    path=path,
                    date=m['date'],
                    imdbid=m['imdbid'],
                    poster=os.path.join("posters", poster_name)
                )
                return
            else:
                Movie.objects.create(
                    title=name,
                    path=path,
                )
        except IntegrityError:
            print("Can't insert add", name, "to the database")

    def save_poster(self, poster_url):
        if not poster_url:
            return ""
        with urlopen(poster_url) as request:
            filename = os.path.basename(poster_url)
            with open(os.path.join(settings.MEDIA_ROOT, "posters", filename), "wb") as f:
                f.write(request.read())
                return filename


class Command(BaseCommand):
    help = "Update local movie list"

    def handle(self, *args, **options):
        crawler = Crawler()
        crawler.crawl('/data/Films')

    def convert_name(self, name):
        name = name.lower()
        name = re.sub('1080p|720p', '', name)
        name = re.sub('bluray|brrip|brrip', '', name)
        name = re.sub('|'.join(UPLOADERS), '', name)
        name = re.sub('x264|H264|\+hi|aac|h.264', '', name, re.IGNORECASE)
        name = re.sub('5.1|7.1', '', name)
        name = re.sub('(19|20)[0-9]{2}', '', name)
        name = re.sub('extended|remastered', '', name)
        name = re.sub('\.', ' ', name)
        return name.strip()

    def download_poster(self, name, poster_url):
        pass
