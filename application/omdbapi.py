import asyncio
import json
import os

import aiohttp
import guessit

from application.models import Movie, NewMovieNotification, MovieDirectory
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlencode

def write_file(filename, data):
    with open(os.path.join(settings.MEDIA_ROOT, "posters", filename), "wb") as f:
        f.write(data)


async def save_poster(poster_url, loop, aiohttp_session):
    if not poster_url:
        return ""

    async with aiohttp_session.get(poster_url) as resp:
        filename = os.path.basename(poster_url)
        loop.call_soon(write_file, filename, await resp.read())
        return os.path.join("posters", filename)  # return media url


class OMDBAPI:
    def __init__(self, loop, aiohttp_session):
        self.loop = loop
        self.aiohttp_session = aiohttp_session

    async def search(self, name):
        infos = guessit.guessit(name)
        if not infos.get('title'):
            return
        try:
            params = urlencode({'s': infos['title'], 'y': infos['year'], 'type': 'movie', 'r': 'json'})
        except KeyError:
            params = urlencode({'s': infos['title'], 'type': 'movie', 'r': 'json'})
        url = 'http://www.omdbapi.com/?%s' % params

        async with self.aiohttp_session.get(url) as resp:
            data = await resp.text()
            print(url, data)
            resp = json.loads(data)
            if "Search" in resp:
                for res in resp['Search']:
                    poster = res['Poster'] if res['Poster'] != 'N/A' else ""
                    return Movie(
                        title=res['Title'],
                        imdbid=res['imdbID'],
                        poster=await save_poster(poster, self.loop, self.aiohttp_session),
                    )

    async def get_detailled_infos(self, imdbid):
        params = urlencode({'i': imdbid, 'plot': 'full', 'r': 'json'})
        url = 'http://www.omdbapi.com/?%s' % params
        async with self.aiohttp_session.get(url) as resp:
            resp = json.loads(await resp.text())
            if resp['Response'] == 'True':
                return resp
