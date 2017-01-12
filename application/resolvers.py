import asyncio
import os
import re
import subprocess

import av
import guessit

from application.models import Movie, NewMovieNotification, MovieDirectory, Subtitle
from application.omdbapi import OMDBAPI
from django.conf import settings
from word2number import w2n


class Resolver:
    SUBRESOLVERS = []

    def __init__(self, loop, aiohttp_session):
        self.loop = loop
        self.aiohttp_session = aiohttp_session

    async def resolve(self, path, movie):
        for klass in self.SUBRESOLVERS:
            inst = klass(self.loop, self.aiohttp_session)
            movie = await inst.resolve(path, movie)
        return movie


class OMDBBaseResolver(Resolver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = OMDBAPI(self.loop, self.aiohttp_session)


class OMDBFilenameResolver(OMDBBaseResolver):
    async def resolve(self, path, movie):
        if movie.title and movie.poster:
            return movie
        name, ext = os.path.splitext(os.path.basename(path))
        name = name.replace('&', '')
        match = await self.api.search(os.path.basename(path))
        if match:
            movie.title = match.title
            movie.imdbid = match.imdbid
            movie.poster = match.poster
        return movie


class OMDBDirnameResolver(OMDBBaseResolver):
    async def resolve(self, path, movie):
        if movie.title and movie.poster:
            return movie
        name = os.path.basename(os.path.dirname(path))
        name = name.replace('&', '')
        match = await self.api.search(name)
        if match:
            movie.title = match.title
            movie.imdbid = match.imdbid
            movie.poster = match.poster
        return movie


class OMDBDetailResolver(OMDBBaseResolver):
    async def resolve(self, path, movie):
        if not movie.imdbid:
            return movie
        infos = await self.api.get_detailled_infos(movie.imdbid)
        if infos.get('Plot') and not movie.plot:
            movie.plot = infos.get('Plot')
        return movie


class OMDBBullshitStripperResolver(OMDBBaseResolver):
    SUBRESOLVERS = [
        OMDBFilenameResolver,
        OMDBDirnameResolver
    ]
    async def resolve(self, path, movie):
        if movie.title:
            return movie

        path = re.sub('remastered|extended|unrated', '', path, flags=re.I)
        return await super().resolve(path, movie)


class OMDBWord2number(OMDBBaseResolver):
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


class SubtitleResolver(Resolver):
    async def resolve(self, path, movie):
        with os.scandir(os.path.dirname(path)) as it:
            for entry in it:
                if entry.is_file():
                    await self.import_sub(entry.path, movie)
        return movie

    async def import_sub(self, path, movie):
        movie.save() # Make sure movie object is created

        name, ext = os.path.splitext(os.path.basename(path))
        if path in [s.path for s in movie.subtitles.all()]:
            return;

        if ext == '.srt':
            dest_dir = os.path.join(settings.MEDIA_ROOT, 'subtitles', str(movie.pk))
            dest = os.path.join(dest_dir, "%s.vtt" % name)
            rel_name = os.path.join('subtitles', str(movie.pk), "%s.vtt" % name)

            if not os.path.isdir(dest_dir):
                print("Creating ouput dir %s" % dest_dir)
                os.makedirs(dest_dir)

            proc = await asyncio.create_subprocess_exec('ffmpeg', '-nostdin', '-i', path, dest)
            await proc.wait()

            #subprocess.call(['ffmpeg', '-nostdin', '-i', path, dest])
            sub = Subtitle(path=path,
                            vtt_file=rel_name,
                            name=name,
                            movie=movie)

        else:
            return

        movie.subtitles.add(sub, bulk=False)


class SubdirectorySubtitleResolver(SubtitleResolver):
    async def resolve(self, path, movie):
        import_dirs = []
        with os.scandir(os.path.dirname(path)) as it:
            for entry in it:
                if entry.is_dir() and entry.name.lower() in ['subs', 'subtitles']:
                    import_dirs.append(entry.path)

        for importpath in import_dirs:
            with os.scandir(importpath) as it:
                for entry in it:
                    if entry.is_file():
                        await self.import_sub(entry.path, movie)
        return movie

class DefaultResolver(Resolver):
    async def resolve(self, path, movie):
        if movie.title:
            return movie
        #Report.fail += 1
        name, ext = os.path.splitext(os.path.basename(path))
        infos = guessit.guessit(name)
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
        SubtitleResolver,
        SubdirectorySubtitleResolver,
        DefaultResolver
    ]

