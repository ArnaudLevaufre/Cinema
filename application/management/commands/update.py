import os
import json
import datetime
import re
from word2number import w2n
from guessit import guess_movie_info
from urllib.request import urlopen
from urllib.parse import urlencode
from django.core.management.base import BaseCommand
from application.models import Movie
from django.conf import settings
from django.db.utils import IntegrityError

MOVIES_EXT = [
    '.mp4',
    '.mkv',
    '.avi',
]

def save_poster(poster_url):
    if not poster_url:
        return ""
    with urlopen(poster_url) as request:
        filename = os.path.basename(poster_url)
        with open(os.path.join(settings.MEDIA_ROOT, "posters", filename), "wb") as f:
            f.write(request.read())
            return os.path.join("posters", filename)  # return media url

class Report:
    fail = 0
    success = 0
    poster = 0

    @staticmethod
    def display():
        total = Report.fail + Report.success
        print("")
        print("Crawler report")
        print("===============")

        print("")
        print("Success {:>5} ({:>6.2f}%)".format(Report.success, Report.success/total*100))
        print("Posters {:>5} ({:>6.2f}%)".format(Report.poster, Report.poster/total*100))
        print("Fails   {:>5} ({:>6.2f}%)".format(Report.fail, Report.fail/total*100))

        print("")
        print("Total   {:>5}".format(total))


class OMDBAPI:
    @staticmethod
    def search(name):
        infos = guess_movie_info(name)
        if not infos.get('title'):
            return
        try:
            params = urlencode({'s': infos['title'], 'y': infos['year'], 'type': 'movie', 'r': 'json'})
        except KeyError:
            params = urlencode({'s': infos['title'], 'type': 'movie', 'r': 'json'})
        url = 'http://www.omdbapi.com/?%s' % params
        with urlopen(url) as request:
            resp = json.loads(request.read().decode())
            if "Search" in resp:
                for res in resp['Search']:
                    infos = OMDBAPI.get_detailled_infos(res['imdbID'])
                    poster = res['Poster']
                    res = infos
                    try:
                        date = datetime.date(int(res['Year']), 1, 1)
                    except ValueError:
                        date = None
                    poster = res['Poster'] if res['Poster'] != 'N/A' else ""
                    yield Movie(
                        title=res['Title'],
                        date=date,
                        imdbid=res['imdbID'],
                        poster=save_poster(poster),
                        plot=res['Plot']
                    )
    @staticmethod
    def get_detailled_infos(imdbid):
        params = urlencode({'i': imdbid, 'plot': 'full', 'r': 'json'})
        url = 'http://www.omdbapi.com/?%s' % params
        with urlopen(url) as request:
            resp = json.loads(request.read().decode())
            if resp['Response'] == 'True':
                return resp


class Resolver:
    def resolve(self, name):
        raise NotImplementedError


class OMDBFilenameResolver(Resolver):
    def resolve(self, path):
        name, ext = os.path.splitext(os.path.basename(path))
        name = name.replace('&', '')
        match = OMDBAPI.search(os.path.basename(path))
        for m in match:
            Report.success += 1
            return m


class OMDBDirnameResolver(Resolver):
    def resolve(self, path):
        name = os.path.basename(os.path.dirname(path))
        name = name.replace('&', '')
        match = OMDBAPI.search(name)
        for m in match:
            Report.success += 1
            return m


class OMDBBullshitStripperResolver(OMDBFilenameResolver):
    PARENT_RESOLVERS = [
        OMDBFilenameResolver,
        OMDBDirnameResolver
    ]
    def resolve(self, path):
        path = re.sub('remastered|extended|unrated', '', path, flags=re.I)
        for resolver in self.PARENT_RESOLVERS:
            r = resolver()
            result = r.resolve(path)
            if result:
                Report.success += 1
                return result


class OMDBWord2number(Resolver):
    PARENT_RESOLVERS = [
        OMDBFilenameResolver,
        OMDBDirnameResolver
    ]
    def resolve(self, path):
        words = path.split()
        for i, word in enumerate(words):
            try:
                if w2n.word_to_num(word):
                    words[i] = str(w2n.word_to_num(word))
            except IndexError:
                pass
        path = ' '.join(words)
        print(path)
        for resolver in self.PARENT_RESOLVERS:
            r = resolver()
            result = r.resolve(path)
            if result:
                Report.success += 1
                return result


class DefaultResolver(Resolver):
    def resolve(self, path):
        Report.fail += 1
        name, ext = os.path.splitext(os.path.basename(path))
        infos = guess_movie_info(name)
        if infos.get('title'):
            return Movie(title=infos['title'])
        else:
            return Movie(title=name)


class ResolverSet:
    RESOLVERS = [
        OMDBFilenameResolver,
        OMDBDirnameResolver,
        OMDBBullshitStripperResolver,
        OMDBWord2number,
        DefaultResolver
    ]
    def resolve(self, path):
        for resolver in self.RESOLVERS:
            r = resolver()
            result = r.resolve(path)
            print("Resolving %s with %s" % (path, r))
            if result:
                return result


class Crawler:

    def __init__(self, cmd):
        self.command = cmd
        self.movies = [m.path for m in Movie.objects.all()]
        self.resolver_set = ResolverSet()

    def crawl(self, path):
        for dirname, subdirs, files in os.walk(path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                path = os.path.join(dirname, filename)
                if ext not in MOVIES_EXT:
                    self.message(self.command.style.WARNING("UNSUPPORTED EXTENSION %s" % ext), path)
                    continue
                statinfo = os.stat(path)
                if statinfo.st_size < 256 * 2**20:  # size < 256MB
                    self.message(self.command.style.WARNING("SAMPLE"), path)
                    continue
                self.handle_file(name, path)



    def message(self, tag, message):
        self.command.stdout.write("[ {:^40} ] {}".format(tag, message))


    def handle_file(self, name, path):
        if path in self.movies:
            self.message(self.command.style.SUCCESS("ALREADY IN DB"), path)
            return

        movie = self.resolver_set.resolve(path)
        if not movie.poster:
            self.message(self.command.style.NOTICE('NO POSTER'), path)
        else:
            Report.poster += 1
        try:
            movie.path = path
            movie.save()
            self.message(self.command.style.SUCCESS("ADDED"), "%s as %s" % (path, movie.title))
        except IntegrityError:
            self.message(self.command.style.ERROR("DB ERROR"), path)

    def save_poster(self, poster_url):
        if not poster_url:
            return ""
        with urlopen(poster_url) as request:
            filename = os.path.basename(poster_url)
            with open(os.path.join(settings.MEDIA_ROOT, "posters", filename), "wb") as f:
                f.write(request.read())
                return filename

    def symlink(self, path):
        destination = os.path.join(settings.MEDIA_ROOT, 'films', os.path.basename(path))
        if os.path.islink(destination):
            os.remove(destination)
        os.symlink(path, destination)


class Command(BaseCommand):
    help = "Update local movie list"

    def handle(self, *args, **options):
        crawler = Crawler(self)
        crawler.crawl('/data/Films')
        Report.display()
