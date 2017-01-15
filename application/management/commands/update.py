import os
import json
import datetime
import re
import asyncio
import aiohttp
from urllib.request import urlopen
from urllib.parse import urlencode
from django.core.management.base import BaseCommand
from application.models import Movie, NewMovieNotification, MovieDirectory
from django.conf import settings
from django.utils import timezone
from application.resolvers import ResolverSet

MOVIES_EXT = [
    '.mp4',
    '.mkv',
    '.avi',
    '.flv',
    '.mov',
    '.webm',
]


class Report:
    def __init__(self):
        self.fail = 0
        self.success = 0
        self.poster = 0
        self.start_time = None

    def start(self):
        Report.start_time = datetime.datetime.now()


    def display(self):
        total_time = datetime.datetime.now() - Report.start_time
        total = self.fail + self.success
        if not total:
            print("You media directory ({}) does not contain any new film.".format(list(MovieDirectory.objects.all())))
            return
        print("")
        print("Crawler report")
        print("===============")

        print("")
        print("Success {:>5} ({:>6.2f}%)".format(self.success, self.success/total*100))
        print("Posters {:>5} ({:>6.2f}%)".format(self.poster, self.poster/total*100))
        print("Fails   {:>5} ({:>6.2f}%)".format(self.fail, self.fail/total*100))

        print("")
        print("Total   {:>5}".format(total))
        print("Time    {}".format(total_time))


class Crawler:

    def __init__(self, cmd, loop, aiohttp_session, report):
        self.command = cmd
        self.loop = loop
        self.aiohttp_session = aiohttp_session
        self.report = report
        self.movies = {m.path: m for m in Movie.objects.all()}
        self.resolver_set = ResolverSet(loop, aiohttp_session)

    def queue_update_tasks(self, movie_directory, tasks):
        path = movie_directory.path

        for dirname, subdirs, files in os.walk(path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                path = os.path.join(dirname, filename)
                if ext not in MOVIES_EXT:
                    self.loop.call_soon(self.message, self.command.style.WARNING("UNSUPPORTED EXTENSION %s" % ext), path)
                    continue
                statinfo = os.stat(path)
                if statinfo.st_size < 256 * 2**20:  # size < 256MB
                    self.loop.call_soon(self.message, self.command.style.WARNING("SAMPLE"), path)
                    continue
                tasks.append(asyncio.ensure_future(self.handle_file(name, path)))

    def message(self, tag, message):
        try:
            self.command.stdout.write("[ {:^40} ] {}".format(tag, message))
        except UnicodeEncodeError:
            pass

    async def handle_file(self, name, path):
        if path in self.movies.keys():
            if not settings.ALLOW_DB_UPDATE:
                return
            # update old movies data.
            movie = self.movies[path]
            update = True
        else:
            movie = Movie()
            update = False

        movie = await self.resolver_set.resolve(path, movie)

        if not movie.poster:
            self.loop.call_soon(self.message, self.command.style.NOTICE('NO POSTER'), path)
        else:
            self.report.poster += 1

        self.report.success += 1
        movie.path = path

        self.loop.call_soon(movie.save)
        if not update:
            self.loop.call_soon(NewMovieNotification.notify_all, movie)
            self.loop.call_soon(self.symlink, path)
            self.loop.call_soon(self.message, self.command.style.SUCCESS("ADDED"), "%s as %s" % (path, movie.title))
        else:
            self.loop.call_soon(self.message, self.command.style.SUCCESS("UPDATED"), "%s as %s" % (path, movie.title))

    def symlink(self, path):
        destination = os.path.join(settings.MEDIA_ROOT, 'films', os.path.basename(path))
        if os.path.islink(destination):
            os.remove(destination)
        os.symlink(path, destination)


class Command(BaseCommand):
    help = "Update local movie list"

    def handle(self, *args, **options):
        report = Report()
        report.start()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        connector = aiohttp.TCPConnector(limit=settings.AIOHTTP_LIMIT, force_close=True, loop=loop)
        aiohttp_session = aiohttp.ClientSession(loop=loop, connector=connector)
        tasks = []

        crawler = Crawler(self, loop, aiohttp_session, report)

        for directory in MovieDirectory.objects.all():
            crawler.queue_update_tasks(directory, tasks)

        loop.run_until_complete(asyncio.wait(tasks))
        aiohttp_session.close()
        loop.close()

        # Delete movies with no path. Those entries are made possible since
        # movies can be saved in the resolvers.
        Movie.objects.filter(path="").delete()

        report.display()
