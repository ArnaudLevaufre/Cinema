import os
import re

from application.models import Movie, NewMovieNotification, MovieDirectory
from application.omdbapi import OMDBAPI
from guessit import guess_movie_info
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
        if movie.title:
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
        if movie.title:
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


class DefaultResolver(Resolver):
    async def resolve(self, path, movie):
        if movie.title:
            return movie
        #Report.fail += 1
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

