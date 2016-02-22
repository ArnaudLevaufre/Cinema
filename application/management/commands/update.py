import os
import json
import datetime
import re
import asyncio
import aiohttp
from word2number import w2n
from guessit import guess_movie_info
from urllib.request import urlopen
from urllib.parse import urlencode
from django.core.management.base import BaseCommand
from application.models import Movie, NewMovieNotification, MovieDirectory
from django.conf import settings
from django.utils import timezone

MOVIES_EXT = [
    '.mp4',
    '.mkv',
    '.avi',
    '.flv',
    '.mov',
    '.webm',
]

def write_file(filename, data):
    with open(os.path.join(settings.MEDIA_ROOT, "posters", filename), "wb") as f:
        f.write(data)


async def save_poster(poster_url):
    if not poster_url:
        return ""
    loop = asyncio.get_event_loop()
    async with OMDBAPI.client.get(poster_url) as resp:
        filename = os.path.basename(poster_url)
        loop.call_soon(write_file, filename, await resp.read())
        return os.path.join("posters", filename)  # return media url

class Report:
    fail = 0
    success = 0
    poster = 0
    started = False
    start_time = None


    @staticmethod
    def start():
        Report.started = True
        Report.start_time = datetime.datetime.now()
        Report.fail = 0
        Report.poster = 0
        Report.success = 0


    @staticmethod
    def display():
        Report.started = False
        total_time = datetime.datetime.now() - Report.start_time
        total = Report.fail + Report.success
        if not total:
            print("You media directory ({}) does not contain any new film.".format(list(MovieDirectory.objects.all())))
            return
        print("")
        print("Crawler report")
        print("===============")

        print("")
        print("Success {:>5} ({:>6.2f}%)".format(Report.success, Report.success/total*100))
        print("Posters {:>5} ({:>6.2f}%)".format(Report.poster, Report.poster/total*100))
        print("Fails   {:>5} ({:>6.2f}%)".format(Report.fail, Report.fail/total*100))

        print("")
        print("Total   {:>5}".format(total))
        print("Time    {}".format(total_time))


class OMDBAPI:
    client = None
    @staticmethod
    async def search(name):
        infos = guess_movie_info(name)
        if not infos.get('title'):
            return
        try:
            params = urlencode({'s': infos['title'], 'y': infos['year'], 'type': 'movie', 'r': 'json'})
        except KeyError:
            params = urlencode({'s': infos['title'], 'type': 'movie', 'r': 'json'})
        url = 'http://www.omdbapi.com/?%s' % params

        async with OMDBAPI.client.get(url) as resp:
            resp = json.loads(await resp.text())
            if "Search" in resp:
                for res in resp['Search']:
                    poster = res['Poster'] if res['Poster'] != 'N/A' else ""
                    return Movie(
                        title=res['Title'],
                        imdbid=res['imdbID'],
                        poster=await save_poster(poster),
                    )

    @staticmethod
    async def get_detailled_infos(imdbid):
        params = urlencode({'i': imdbid, 'plot': 'full', 'r': 'json'})
        url = 'http://www.omdbapi.com/?%s' % params
        async with OMDBAPI.client.get(url) as resp:
            resp = json.loads(await resp.text())
            if resp['Response'] == 'True':
                return resp


class Resolver:
    SUBRESOLVERS = []
    async def resolve(self, path, movie):
        for klass in self.SUBRESOLVERS:
            inst = klass()
            movie = await inst.resolve(path, movie)
        return movie


class OMDBFilenameResolver(Resolver):
    async def resolve(self, path, movie):
        if movie.title:
            return movie
        name, ext = os.path.splitext(os.path.basename(path))
        name = name.replace('&', '')
        match = await OMDBAPI.search(os.path.basename(path))
        if match:
            Report.success += 1
            movie.title = match.title
            movie.imdbid = match.imdbid
            movie.poster = match.poster
        return movie


class OMDBDirnameResolver(Resolver):
    async def resolve(self, path, movie):
        if movie.title:
            return movie
        name = os.path.basename(os.path.dirname(path))
        name = name.replace('&', '')
        match = await OMDBAPI.search(name)
        if match:
            Report.success += 1
            movie.title = match.title
            movie.imdbid = match.imdbid
            movie.poster = match.poster
        return movie


class OMDBDetailResolver(Resolver):
    async def resolve(self, path, movie):
        if not movie.imdbid:
            return movie
        infos = await OMDBAPI.get_detailled_infos(movie.imdbid)
        if infos.get('Plot') and not movie.plot:
            movie.plot = infos.get('Plot')
        return movie


class OMDBBullshitStripperResolver(Resolver):
    SUBRESOLVERS = [
        OMDBFilenameResolver,
        OMDBDirnameResolver
    ]
    async def resolve(self, path, movie):
        if movie.title:
            return movie

        path = re.sub('remastered|extended|unrated', '', path, flags=re.I)
        return await super().resolve(path, movie)


class OMDBWord2number(Resolver):
    SUBRESOLVERS = [
        OMDBFilenameResolver,
        OMDBDirnameResolver
    ]
    async def resolve(self, path, movie):
        if movie.title:
            return movie
        words = path.split()
        for i, word in enumerate(words):
            try:
                if w2n.word_to_num(word):
                    words[i] = str(w2n.word_to_num(word))
            except IndexError:
                pass
        path = ' '.join(words)
        return await super().resolve(path, movie)


class DefaultResolver(Resolver):
    async def resolve(self, path, movie):
        if movie.title:
            return movie
        Report.fail += 1
        name, ext = os.path.splitext(os.path.basename(path))
        infos = guess_movie_info(name)
        if infos.get('title'):
            return Movie(title=infos['title'])
        else:
            return Movie(title=name)


class ResolverSet(Resolver):
    SUBRESOLVERS = [
        OMDBFilenameResolver,
        OMDBDirnameResolver,
        OMDBBullshitStripperResolver,
        OMDBWord2number,
        OMDBDetailResolver,
        DefaultResolver
    ]


class Crawler:

    def __init__(self, cmd):
        self.command = cmd
        self.movies = [m.path for m in Movie.objects.all()]
        self.resolver_set = ResolverSet()

    def crawl(self, movie_directory):
        path = movie_directory.path

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session = OMDBAPI.client = aiohttp.ClientSession(loop=loop)
        tasks = []
        for dirname, subdirs, files in os.walk(path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                path = os.path.join(dirname, filename)
                if ext not in MOVIES_EXT:
                    loop.call_soon(self.message, self.command.style.WARNING("UNSUPPORTED EXTENSION %s" % ext), path)
                    continue
                statinfo = os.stat(path)
                if statinfo.st_size < 256 * 2**20:  # size < 256MB
                    loop.call_soon(self.message, self.command.style.WARNING("SAMPLE"), path)
                    continue
                tasks.append(asyncio.ensure_future(self.handle_file(name, path)))

        loop.run_until_complete(asyncio.wait(tasks))
        OMDBAPI.client.close()
        loop.close()

    def message(self, tag, message):
        try:
            self.command.stdout.write("[ {:^40} ] {}".format(tag, message))
        except UnicodeEncodeError:
            pass


    async def handle_file(self, name, path):
        loop = asyncio.get_event_loop()
        if path in self.movies:
            loop.call_soon(self.message, self.command.style.SUCCESS("ALREADY IN DB"), path)
            return

        movie = await self.resolver_set.resolve(path, Movie())

        if not movie.poster:
            loop.call_soon(self.message, self.command.style.NOTICE('NO POSTER'), path)
        else:
            Report.poster += 1

        movie.path = path

        loop.call_soon(movie.save)
        loop.call_soon(NewMovieNotification.notify_all, movie)
        loop.call_soon(self.symlink, path)
        loop.call_soon(self.message, self.command.style.SUCCESS("ADDED"), "%s as %s" % (path, movie.title))

    def symlink(self, path):
        destination = os.path.join(settings.MEDIA_ROOT, 'films', os.path.basename(path))
        if os.path.islink(destination):
            os.remove(destination)
        os.symlink(path, destination)


class Command(BaseCommand):
    help = "Update local movie list"

    def handle(self, *args, **options):
        Report.start()
        crawler = Crawler(self)

        for d in MovieDirectory.objects.all():
            crawler.crawl(d)

        Report.display()
