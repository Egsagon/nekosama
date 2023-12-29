'''
Core module for the API.
'''

import re
import json
import base64
import requests

from nekosama import utils
from nekosama import consts
from nekosama import download

from time import sleep
from typing import Callable


class Episode:
    def __init__(self,
                 url: str,
                 data: dict = None,
                 anime: 'Anime' = None,
                 session: requests.Session = None) -> None:
        '''
        Represents an Anime episode.
        
        
        Arguments
            url: the Episode url.
        '''
        
        self.url = url
        self.anime = anime
        self.session = session or requests.Session()
        
        self.cache = {}
        self.providers = []
        
        self.cached_data = data
        
        self.info = utils.parse_url(self.url)
        
        # Error protection
        if self.info['type'] != 'episode':
            raise Exception('Invalid URL', url)
        
        self.id = self.info['id']
        self.name = self.info['name']
        self.lang = self.info['lang'].upper()
    
    def __repr__(self) -> str:
        return f'nekosama.Episode(name={self.anime.name}, index={self.index})'
    
    def get(self,
            url: str,
            headers: dict = None,
            cache: bool = True) -> requests.Response:
        '''
        Get a page from the cache or fetch it.
        
        Arguments
            url: the url to request
            headers: the headers of the request
            cache: whether to use cache for fetching.
        '''
        
        if cache and url in self.cache:
            return self.cache.get(url)
        
        req = self.session.get(url, headers = headers)
        
        # Error protection
        if not req.ok:
            raise ConnectionError(req.status_code, req.content)
        
        self.cache[url] = req
        return req
    
    def clear_cache(self, all: bool = True) -> None:
        '''
        Clear the instance cache.
        
        Arguments
            all: whether to clear all caches.
                 if False, the data cache will be kept.
        '''
        
        # Clear request and urls caches
        self.cache.clear()
        self.providers.clear()
        
        # Clear the data cache
        if not all:
            self.cached_data.clear()
    
    @property
    def data(self) -> dict[str]:
        '''
        Get the available data for this episode.
        '''
        
        if self.cached_data is not None:
            return self.cached_data
        
        anime_url = None
        
        if (ani := self.anime) is not None:
            # Get the anime url from superior
            anime_url = ani.url
        
        else:
            # Find the anime url in the page
            raw = self.get(self.url).text
            url = re.findall(consts.re.an_from_ep, raw)[0]
            anime_url = consts.root + url
        
        src = self.anime.get(anime_url).text
        data = json.loads(re.findall(consts.re.ep_list, src)[0])
        
        # Search the episode
        for ep in data:
            if ep['url'] in self.url:
                self.cached_data = ep
                return ep
        
        raise Exception('Failed to get episode data')
    
    @property
    def time(self) -> int:
        '''
        The episode duration (in minutes).
        '''
        
        if self.data is None: self.get_data()
        return int(self.data['time'].split(' ')[0])
    
    @property
    def title(self) -> str:
        '''
        The episode title. For path naming,
        use Episode.name.
        '''
        
        if self.data is None: self.get_data()
        return self.data['title']
    
    @property
    def index(self) -> int:
        '''
        The episode index in the anime.
        '''
        
        # NOTE - We could use the get_date method
        # but that can also be done with a regex.
        
        # if self.data is None: self.get_data()
        # return self.data['num']
        
        return int(re.findall(consts.re.ep_index, self.url)[0])
    
    @property
    def image(self) -> str:
        '''
        The image url.
        '''
         
        if self.data is None: self.get_data()
        return self.data['url_image']
    
    def download_image(self, path: str) -> None:
        '''
        Download the episode image.
        
        Arguments
            path: the path to download to.
        '''
        
        raw = self.get(self.image).content
        
        with open(path, 'wb') as output:
            output.write(raw)
    
    def get_providers(self) -> list[str]:
        '''
        Get all the available providers for this episode.
        '''
        
        raw = self.get(self.url).text
        
        self.providers = [url.split('= ')[1][1:-2]
                          for url in re.findall(consts.re.providers, raw)]
        
        return self.providers

    def get_fragments(self,
                      provider: str = consts.provider.BEST,
                      quality: str | int = consts.quality.BEST) -> str:
        '''
        Get the raw m3u8 qualities list for this episode.
        '''
        
        # Get provider url (link to the player)
        if not len(self.providers): self.get_providers()
        provider_url = utils.select_provider(self.providers, provider)
        print('[FRAG] Fetched provider', provider)
        
        # Get the provider link to its script
        src = self.get(provider_url , headers = consts.headers).text
        res = re.findall(consts.re.script, src)[0][:-2]
        
        # Get the m3u file url
        src = self.get(res, headers = consts.headers).text
        
        # if provider == consts.provider.FUSE:
        if 'atob' in src: reg = consts.re.new_fuse_json
        else: reg = consts.re.m3u8
        
        # Parse the encoded json
        res = re.findall(reg, src)[0]
        raw = base64.b64decode(res).decode()
        m3u = re.findall(consts.re.m3u8_urls, raw)[0].replace('\\', '')[:-1]
        
        print('[FRAG] Fetched m3u file')
        
        # Get the m3u file data
        src = self.get(m3u, headers = consts.headers).text
        url = utils.select_quality(utils.parse_qualities(src), quality)
        
        # Fetch the fragment list
        return self.get(url, headers = consts.headers).text
    
    def download(self,
                 path: str,
                 provider: str = consts.provider.BEST,
                 quality: str = consts.quality.BEST,
                 method: download.METHOD_TYPE = 'ffmpeg',
                 **kwargs) -> None:
        '''
        Download the episode at a specific path.
        
        Arguments
            path: the path to download to
            provider: the provider to use (constant)
            quality: the quality to use (constant)
            method: the backend to use
            kwargs: backend arguments
        
        Quality type:
            if <int>: get the nearest quality
            if <str>: same as constants
        
        Path formating options:
            {name}: name of the episode
            {index}: index of the episode
            {id}: neko sama id of the episode
        '''
        
        path = utils.ghost_format(
            path,
            name = self.name,
            index = self.index,
            id = self.id
        )
        
        # Get the fragments list
        raw = self.get_fragments(provider, quality)
        
        # Start the download
        backend = download.reach(method)
        # print('Using backend', backend)
        
        try:
            print(f'[ EP ] Downloading episode {self.index}')
            backend(raw = raw, path = path, **kwargs)
        
        except Exception as err:
            
            # TODO
            raise err

    def to_dict(self, lazy: bool = False) -> dict:
        '''
        Return a serialized version of the object.
        TODO - lazy
        '''
        
        keys = ['name', 'title', 'image', 'time', 'id', 'lang', 'url']
        
        return {key: getattr(self, key) for key in keys}

class Anime:
    def __init__(self,
                 url: str,
                 session: requests.Session = None) -> None:
        '''
        Represents an anime containing one or multiple episodes.
        
        Arguments
            url: the anime page url
        '''
        
        self.url = url
        self.info = utils.parse_url(self.url)
        
        # Error protection
        if self.info['type'] != 'anime':
            raise Exception('Invalid url', url)
        
        self.name = self.info['name']
        self.id = self.info['id']
        self.lang = self.info['lang']
        
        self.session = session or requests.Session()
        self.cache = {}
        
        self.cached_episodes = []
    
    def __repr__(self) -> str:
        return f'nekosama.Anime(name={self.name})'
    
    def get(self,
            url: str,
            headers: dict = None,
            cache: bool = True) -> requests.Response:
        '''
        Get a page from the cache or fetch it.
        
        Arguments
            url: the url to request
            headers: the headers of the request
            cache: whether to use cache for fetching.
        '''
        
        if cache and url in self.cache:
            return self.cache.get(url)
        
        req = self.session.get(url, headers = headers)
        
        # Error protection
        if not req.ok: raise ConnectionError(req.status_code, req.content)
        
        self.cache[url] = req
        return req
    
    def clear_cache(self, all: bool = True) -> None:
        '''
        Clear the instance cache.
        
        Arguments
            all: whether to clear all caches.
                 if False, the episodes cache will be kept.
        '''
        
        self.cache.clear()
        if not all: self.cached_episodes.clear()
    
    @property
    def data(self) -> dict[str]:
        '''
        Get anime useful data.
        '''
        
        raw = self.get(self.url).text
        return {k: v for k, v in re.findall(consts.re.ani_props, raw)}
    
    @property
    def title(self) -> str:
        '''
        The anime title.
        '''
        
        return self.data['title'].replace(' | Neko-sama', '')
    
    @property
    def description(self) -> str:
        '''
        The raw anime description.
        '''
        
        return self.data['description']
    
    @property
    def tags(self) -> list[str]:
        '''
        Identification tabs for searching.
        '''
        
        raw = self.get(self.url).text
        tags = set(re.findall(consts.re.ani_tags, raw))
        tags.remove('genres')
        
        return list(tags)
    
    @property
    def image(self) -> str:
        '''
        The image url.
        '''
         
        if self.data is None: self.get_data()
        return self.data['image']
    
    def download_image(self, path: str) -> None:
        '''
        Download the anime image.
        
        Arguments
            path: the path to download to.
        '''
        
        raw = self.get(self.image).content
        
        with open(path, 'wb') as output:
            output.write(raw)
    
    def download_background(self, path: str) -> None:
        '''
        Download the background image of the anime.
        
        Arguments
            path: the path to download to.
        '''
        
        src = self.get(self.url).text
        url = re.findall(consts.re.ep_bg, src)[0]
        raw = self.get(url).content
        
        with open(path, 'wb') as output:
            output.write(raw)
    
    def get_episodes(self) -> list[Episode]:
        '''
        Get all the anime episodes.
        '''
        
        src = self.get(self.url).text
        data = json.loads(re.findall(consts.re.ep_list, src)[0])
        
        eps = []
        for ep in data:
            eps += [Episode(url = consts.root + ep['url'],
                            data = ep,
                            anime = self,
                            session = self.session)]
        
        return eps

    @property
    def episodes(self) -> list[Episode]:
        '''
        Same as get_episodes(),
        but uses cache instead.
        '''
        
        if not len(self.cached_episodes):
            self.cached_episodes = self.get_episodes()
        
        return self.cached_episodes

    def download(self,
                 directory: str,
                 name_format: str = '{name}.mp4',
                 provider: str = consts.provider.BEST,
                 quality: str = consts.quality.BEST,
                 method: download.METHOD_TYPE = 'ffmpeg',
                 timeout = 5,
                 start: int | None = None,
                 end: int | None = None,
                 **kwargs) -> list[str]:
        '''
        Download all the episodes to a directory
        and return all the paths.
        
        Arguments
            directory: the folder to download to.
            name_format: see Episode.download.
            provider, quality, method: backend args.
            timeout: pause between each download.
        
        Returns a list of pathes.
        '''
        
        pathes = []
        
        print(f'[ AN ] Downloading anime {self.title}')
        
        for episode in self.episodes[start:end]:
            
            path = episode.download(
                path = directory + name_format,
                provider = provider,
                quality = quality,
                method = method,
                **kwargs
            )
            
            pathes += [path]
            sleep(timeout)
        
        return pathes

    def to_dict(self, lazy: bool = False) -> dict:
        '''
        Return a serialised version of the object.
        TODO - lazy
        '''
        
        return {
            'url': self.url,
            'name': self.name,
            'id': self.id,
            'title': self.title,
            'lang': self.lang,
            'episodes': len(self.episodes),
            'image': self.image,
            'tags': self.tags,
            'description': self.description,
        }
            

class Client:
    def __init__(self) -> None:
        '''
        Wrapper for both Anime and Episode classes.
        '''
        
        self.session = requests.Session()
        self.cache = {}
    
    def get(self,
            url: str,
            headers: dict = None,
            cache: bool = True) -> requests.Response:
        '''
        Get a page from the cache or fetch it.
        
        Arguments
            url: the url to request
            headers: the headers of the request
            cache: whether to use cache for fetching.
        '''
        
        if cache and url in self.cache:
            return self.cache.get(url)
        
        req = self.session.get(url, headers = headers)
        
        # Error protection
        if not req.ok: raise ConnectionError(req.status_code, req.content)
        
        self.cache[url] = req
        return req
    
    def clear_cache(self) -> None:
        '''
        Clear the instance cache.
        In particular, erase the list of episodes
        to search in.
        '''
        
        self.cache.clear()
    
    def get_anime(self, url: str) -> Anime:
        '''
        Fetch an anime from the website.
        
        Arguments
            url: the url of the anime.
        '''
        
        return Anime(url, self.session)

    def search(self,
               name: str | re.Pattern = '', # TODO pattern
               lang: str | tuple = None,
               type: list[str] = [],
               genres: list[str] = [],
               score: str = None,
               date: str = None,
               limit: int = None,
               iter_limit: int = None,
               filter: Callable[[dict], bool] = None) -> list[Anime]:
        '''
        Search for animes that match a query.
        
        Arguments
            name: the name of the anime or a part of it.
            lang: VOSTFR or VF or a tuple of both.
            type: a list of anime tags ('m0v1e', etc.)
            genres: a list of genres (shounen, action, etc.).
            score: score filter (e.g. '>4').
            date: release date filter (e.g. '>2010' or '2000<{}<2010').
            limit: stop after n animes.
            filter: callable that handle further filtering.
        
        Returns a list of Anime objects.
        '''
        
        # Lang is needed first to retrieve the files
        if lang is None: lang = ('VOSTFR', 'VF')
        if isinstance(lang, str): lang = (lang, )
        
        urls = [consts.root + f'/animes-search-{d.lower()}.json'
                for d in lang]
        
        # Fetch the urls and assemble the file
        file = []
        for url in urls:
            file += json.loads(self.session.get(url).text)
        
        # Build filters
        fdate = utils.fbuild(date)
        fscore = utils.fbuild(score)
        
        matches = []
        for index, anime in enumerate(file):
            
            # Custom filter override
            if filter and filter(anime):
                matches += [anime]
                continue
            
            # Iteration limit
            if iter_limit and index >= iter_limit: break
            
            # Result limit
            if limit and len(matches) >= limit: break
            
            # Type filter
            t = anime['type'].lower()
            if len(type) and t and t in type: continue
            
            # Genres filter
            if len(genres):
                for genre in anime['genres']:
                    if not genre in genres: continue
            
            # Score filter
            if not fscore(anime['score']): continue
            
            # Date filter
            if not fdate(anime['start_date_year']): continue
            
            # Check tags
            keys = ['title', 'title_english', 'title_romanji', 'title_french']
            
            for key in keys:
                if name in (anime[key] or '').lower():
                    matches += [anime]
                    break
        
        return [Anime(consts.root + data['url'], self.session) for data in matches]

# EOF