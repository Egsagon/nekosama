import core.utils as utils
import core.log as logging
import core.consts as consts
import core.grabber as grabber

import json
import threading
import requests as req
import requests_html as hreq

from copy import copy
from sys import getsizeof
from time import sleep, time
from dataclasses import dataclass
from typing import Any, Callable, Self
from numerize.numerize import numerize

log = logging.root.new_logger('scrapper')


class EpisodeIterable:
    def __init__(self, anime: 'Anime') -> None:
        '''
        Provide a generator-like object that will
        load episodes one after one.
        -----------------------------------------
        '''
        
        self.anime = anime
    
    def __getitem__(self, index) -> 'Episode':
        '''
        Called when `anime.episode` attribute is called.
        ------------------------------------------------
        
        Arguments
            index: the item index.
            fast: Actuate method to use.
            
        Returns
            An <Episode> object.
        '''
                
        if 1: return self.anime.get_episode(index)
        return self.anime.episodes[index]

    def __repr__(self) -> str:
        '''
        Represents the class.
        '''
        
        return f'<Episode {self.anime.name} (not generated yet)>'

    def __iter__(self) -> Self:
        '''
        Iteration method.
        '''
        
        self.index = 0
        return self
    
    def __next__(self) -> 'Episode':
        '''
        Next iteration method.
        '''
        
        el = self[self.index]
        self.index += 1
        return el


@dataclass
class Image:
    raw: bytes
    ext: str = None
    url: str = None
    
    def __post_init__(self) -> None:
        '''
        Attempt to fetch the image extension.
        -------------------------------------
        '''
        
        self.log = log.new_logger('image')
        
        if self.ext is not None: return
        self.ext = utils.get_extension(self.url)
        
        self.log.log(f'Got extension \033[92m{self.ext}\033[0m for image \033[93m{self}\033[0m')
    
    def __repr__(self) -> str:
        '''
        Represents the class.
        '''
        
        return f'<Image {self.ext}>'
    
    def download(self, path: str, ext: bool = True) -> None:
        '''
        Download the image to a location.
        ---------------------------------
        
        Arguments
            ext: Append the extention at the end of the path.
        '''
        
        if ext: path += '.' + self.ext
        with open(path, 'wb') as f: f.write(self.raw)
        
        self.log.log(f'Downloaded \033[93m{self}\033[0m to \033[92m{path}')

class Episode:
    def __init__(self, url: str, anime: 'Anime') -> None:
        '''
        Represent an anime's episode.
        '''
        
        self.url = url
        self.anime = anime
        self.comm = self.anime.comm
        
        self.raw_name = utils.parse_name(self.url)
        self.name = utils.format_name(self.raw_name)
        
        # Dynamic attributes
        self.picture: bytes = None
        self.poster: bytes = None
        self.tags: dict[str, str] = None
        self.data: dict[str, str] = None
        self.provider: str = None # most used as backend but still here
        
        # Episode page cache
        self.cache: hreq.HTMLSession = None
        
        self.log = logging.root.new_logger('episode')
        # self.log.log(f'Loaded new object \033[93m{self}\033[0m')
    
    def __getattribute__(self, name: str) -> Any:
        '''
        Handle attributes redistribution.
        '''
        
        auto = ['picture', 'poster', 'tags', 'data', 'provider']
        value = super().__getattribute__(name)
        
        # Static attributes
        if name not in auto: return value
        
        # Attributes to generate
        if name in auto and value is None:
            self.log.log(f'Generating \033[92m{name}\033[0m attribute for \033[93m{self}\033[0m')
            return eval(f'self.get_{name}')()
        
        # Attributes already generated
        return value
    
    def __repr__(self) -> str:
        '''
        Represents the class.
        '''
        
        return f'<Episode {self.name}>'
    
    @classmethod
    def from_url(cls, url: str, comm: 'Comm' = None) -> Self:
        '''
        Get an episode given its url.
        -----------------------------
        
        Arguments
            url: the episode url.
            comm: the comm instance if exists.
        '''
        
        # Get the parent anime
        ani_url = utils.get_anime_from_episode_url(url)
        
        # Build the comm, anime and the episode
        return Episode(url, Anime(ani_url, comm or Comm()))
    
    def get_page(self,
                 cache: bool = True,
                 force: bool = False) -> hreq.HTMLResponse:
        '''
        Get the anime page in the cache or fetch it.
        --------------------------------------------
        '''
        
        if self.cache and not force: page = self.cache
        else: page = self.comm.get_dyna(self.url)
        
        if cache: self.cache = page
        return page
    
    def get_picture(self,
                    cache: bool = True,
                    force: bool = False) -> Image:
        '''
        Get the picture of the anime episode.
        -------------------------------------
        '''
        
        page = self.anime.get_page(cache, force)
        
        thumbnails = page.find('.js-list-episode-container .holder')
        
        try:
            for thumbnail in thumbnails:
                
                # Parse <a>
                a = thumbnail.find('a', first = True)
                href = utils.complete_url(a.attrs['href'])
                
                if href != self.url: continue
                
                # parse <img>
                i = thumbnail.find('img', first = True)
                src = i.attrs['src']
                
                # Fetch the image
                raw = self.comm.session.get(src).content
                
                self.log.log(f'Parsed \033[93m{self}\033[0m picture, converting to object')
                return Image(raw, url = src)
        
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m picture:', e.args)
        
        self.log.err(f'Episode \033[93m{self}\033[91m vanished from parent')
    
    def get_provider(self,
                     cache: bool = True,
                     force: bool = False) -> str:
        '''
        Get the provider url for this episode,
        aka the embed url.
        --------------------------------------
        '''
        
        page = self.get_page(cache, force)
        
        # Parse
        try:
            provider = page.find('#display-player iframe', first = True).attrs['src']
            provider_name = provider.split('//')[1].split('/')[0]
        
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m provider:', e.args)
        
        self.log.log(f'Parsed \033[93m{self}\033[0m provider \033[94m{provider_name}\033[0m')
        self.provider = provider
        return provider
    
    def download_old(self,
                 path: str,
                 quality: int | str = consts.Quality.BEST,
                 ext: bool = True,
                 looping_callback: Callable = None,
                 show_bar: bool = True) -> str:
        '''
        Download the episode.
        ---------------------
        
        Arguments
            path: the path to download the episode to.
            quality: the specified quality.
                - if int: will take the nearest quality;
                - if str: either 'best', 'worst' or 'middle'.
            ext: whether to add an extension at the end of the path.
        
        Returns
            the (modified) path.
        '''
        
        # Fetch provider url
        provider_url = self.get_provider()
        
        log.log(f'Fetched provider\033[94m', provider_url)
        
        # Get quality
        raw = grabber.grab_request(provider_url, True)
        
        log.log(f'grabbed provider response\033[92m', raw.split('\n')[0])
        
        url = utils.parse_qualities(raw, quality)
        
        url_rep = (url + ' ' * 20)[:20] + '...'
        
        log.log(f'Using url \033[92m{url_rep}\033[0m with quality \033[92m{quality}\033[0m')
        
        # Fetch segments
        headers = consts.segments_headers
        
        # In case provider is pstream, change host
        if 'www.pstream.net' in provider_url: headers['Host'] = 'www.pstream.net'
        
        res = self.comm.session.get(url, headers = headers).text
        segments = [s for s in res.split('\n') if s.startswith('https://')]
        
        lenght = len(segments)
        
        log.log(f'Fetching \033[92m{lenght}\033[0m segments...')
        
        # Download
        content = bytes()
        
        for i, link in utils.bar('Fetching', list(enumerate(segments)), show_bar):
            
            # log.log(f'Fetching [\033[93m{i: ^{len(str(lenght))}}\033[0m/{lenght}]')
            
            segment = self.comm.session.get(link)
            
            # Error protection
            if not segment.ok:
                raise consts.FetchingErorr(segment.text, segment.status_code)
            
            if looping_callback is not None: looping_callback(i, lenght)
            
            content += segment.content
            
        # Write to file
        log.log(f'Writing \033[93m{self}\033[0m to file...')
        
        if ext: path += '.mp4'
        with open(path, 'wb') as file:
            file.write(content)
        
        return path

    def get_chunks(self, quality: str | int) -> tuple[dict, list]:
        '''
        Get video chunks of the episode according to a quality.
        '''
        
        # Fetch provider url
        provider_url = self.get_provider()
        log.log(f'Fetched provider\033[94m', provider_url)
        
        # Fetch response
        raw = grabber.grab_request(provider_url, True)
        log.log(f'grabbed provider response\033[92m', raw.split('\n')[0])
        
        # Parse quality
        url = utils.parse_qualities(raw, quality)
        url_rep = (url + ' ' * 20)[:20] + '...'
        log.log(f'Using url \033[92m{url_rep}\033[0m with quality \033[92m{quality}\033[0m')
        
        # Build headers
        headers = consts.segments_headers
        if 'www.pstream.net' in provider_url: headers['Host'] = 'www.pstream.net'
        
        # Fetch segments
        res = self.comm.session.get(url, headers = headers).text
        return headers, [s for s in res.split('\n') if s.startswith('https://')]

    def get_chunk(self,
                  request: req.PreparedRequest,
                  data: dict = None,
                  todo: list = None,
                  timeout: int = .05) -> bytes | None:
        '''
        Download one video chunk.
        '''
        
        raw = self.comm.session.send(request).content
        
        while b'<html>' in raw:
            
            # If request fails, put it back in todo
            if todo is not None:
                return todo.append(request)
            
            sleep(timeout)
            raw = self.comm.session.send(request).content
        
        else:
            if data is None: return raw
            key = int(request.url.split('/')[-1].split('.')[0])
            data[key] = raw
    
    def download(self,
                   path: str,
                   quality: int | str = consts.Quality.BEST,
                   ext: bool = True,
                   looping_callback: Callable[[int, int, str], None] = None,
                   timeout: float = .05) -> str:
        '''
        Download the episode to a file,
        with a specified quality.
        -------------------------------
        
        Arguments
            path: the path to download the file to.
            quality: quality to download the video to.
            ext: wheter to include an extension to the file.
            looping_callback: update download log function.
            timeout: spacing between each request. Defaults to server rate limit.
        
        Returns
            The path of the downloaded file.
        '''
        
        # Yes
        if looping_callback is None: looping_callback = lambda *_: None
        
        # Get video chunks and generate requests
        headers, chunks = self.get_chunks(quality)
        requests = [req.Request('GET', chunk, headers).prepare() for chunk in chunks]
        log.log(f'Generated \033[92m{len(requests)}\033[0m requests.')
        
        data = {}
        todo = copy(requests)
        timeout = .05
        
        while len(todo):
            current = todo.pop(0)
            
            t = threading.Thread(target = self.get_chunk,
                                 args = [current, data, todo, timeout])
            t.start()
            sleep(timeout)
            
            # Debug
            ld, lt = len(data), len(todo)
            log.log(f'\rDownloading \033[91m{lt}\033[0m => \033[92m{ld}', end = '')
            looping_callback(len(chunks) - lt, len(chunks), 'Downloading')
        
        log.newline() and log.log('Checking integrity...')
        
        # Check for missing chunks
        for i in range(len(chunks)):
            if not i in data.keys():
                
                # Debug
                log.log(f'Downloading missing chunk at \033[91m{i}')
                looping_callback(i, len(chunks), 'Checking')
                
                # Get chunk request
                mreq = [r for r in requests if r.url.endswith(f'{i}.ts')][0]
                raw = self.get_chunk(mreq, timeout = timeout)
                
                # Add to data
                data[i] = raw
        
        # Write chunks
        if ext: path += '.mp4'
        with open(path, 'wb') as file:
            
            for i in range(len(chunks)):
                raw = data[i]
                log.log(f'\rWriting to file (\033[92m{i + 1}\033[0m)', end = '')
                looping_callback(i, len(chunks), 'Writing')
                file.write(raw)
        
        log.newline()
        log.log(f'Downloaded episode to \033[94m{path}')
        
        return path


class Anime:
    def __init__(self, url: str, comm: 'Comm') -> None:
        '''
        Represent an anime.
        '''
        
        self.url = url
        self.comm = comm
        self.raw_name = utils.parse_name(url)
        self.name: str = utils.format_name(self.raw_name)
        
        # Generated when called
        self.synopsis: str = None
        self.data: dict[str, str] = None
        self.picture: bytes = None
        self.poster: bytes = None
        self.tags: dict[str, str] = None
        
        self.episodes: list[Episode] = None  # fetch all episodes
        self.episode = EpisodeIterable(self) # generator-like object
        
        # Page cache
        self.cache: hreq.HTMLResponse = None
        
        self.log = log.new_logger('anime')
        
        # self.log.log(f'Loaded new object \033[93m{self}\033[0m')
    
    def __getattribute__(self, name: str) -> Any:
        '''
        Handle attributes redistribution.
        '''
        
        auto = ['synopsis', 'data', 'picture',
                'poster', 'tags', 'episodes']
        
        value = super().__getattribute__(name)
        
        # Static attributes
        if name not in auto: return value
        
        # Attributes to generate
        if name in auto and value is None:
            
            if name == 'episodes':    
                self.log.warn(f'Deprecated attribute: \033[91m{name}\033[0m')
            
            self.log.log(f'Generating \033[92m{name}\033[0m attribute for \033[93m{self}\033[0m')
            return eval(f'self.get_{name}')()
        
        # Attributes already generated
        return value
    
    def __repr__(self) -> str:
        '''
        Represents the class.
        '''
        
        return f'<Anime {self.name}>'
    
    def get_page(self,
                     cache: bool = True,
                     force: bool = False) -> hreq.HTMLResponse:
        '''
        Get the anime page in the cache or fetch it.
        --------------------------------------------
        '''
        
        if self.cache and not force: page = self.cache
        else: page = self.comm.get_dyna(self.url)
        
        if cache: self.cache = page
        return page        
    
    def get_synopsis(self,
                     cache: bool = True,
                     force: bool = False) -> str:
        '''
        Get the anime's synopsis.
        -------------------------
        
        Arguments
            cache: whether to save the fetched data to cache.
            force: whether to use already cached data.
        
        Returns
            A string containing the synopsis.
        '''
        
        # Load from cache or fetch
        page = self.get_page(cache, force)
        
        # Find synopsis on the page
        try:
            syn = page.find('.synopsis', first = 1).text
        
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m data:', e.args)
            
        
        self.log.log(f'Parsed \033[93m{self}\033[0m synopsis')
        self.synopsis = syn
        return syn

    def get_data(self,
                 cache: bool = True,
                 force: bool = False) -> dict[str, str]:
        '''
        Get the anime data.
        -------------------
        
        Returns
            A dict referencing values to their data field.
        '''
        
        # Load from cache or fetch
        page = self.get_page(cache, force)
        
        data = {}
        elements = page.find('#anime-info-list .item')
        
        try:
            # Parse data
            for el in elements:
                raw: str = el.text
                
                k, *v = raw.split('\n' if '\n' in raw else None)
                data[k] = ' '.join(v)
            
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m data:', e.args)
        
        self.log.log(f'Parsed \033[93m{self}\033[0m data')
        self.data = data
        return data

    def get_picture(self,
                    cache: bool = True,
                    force: bool = False) -> Image:
        '''
        Get the picture of the anime.
        -----------------------------
        
        Arguments
            path: if provided, will download the picture to it.
        
        Returns
            if path is not provided, return the image bytes.
        '''
        
        page = self.get_page(cache, force)
        
        try:
            src = page.find('.loading', first = True).attrs['src']
            raw = self.comm.session.get(src).content
        
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m picture:', e.args)
        
        self.log.log(f'Parsed \033[93m{self}\033[0m picture, converting to object')
        return Image(raw, url = src)
    
    def get_poster(self,
                   cache: bool = True,
                   force: bool = False) -> Image:
        '''
        Get the poster of the anime.
        -----------------------------
        
        Arguments
            path: if provided, will download the poster to it.
        
        Returns
            if path is not provided, return the image bytes.
        '''
        
        page = self.get_page(cache, force)
        
        try:
            style = page.find('#head', first = True).attrs['style']
            src = style.split('url(')[1].split(')')[0]
        
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m poster:', e.args)
        
        self.log.log(f'Parsed \033[93m{self}\033[0m poster')
        raw = self.comm.session.get(src).content
        return Image(raw, url = src)
    
    def get_tags(self,
                 cache: bool = True,
                 force: bool = False) -> dict[str, str]:
        '''
        Get the anime search tags.
        --------------------------
        
        Returns
            A dict referencing tag urls to their name.
        '''
        
        page = self.get_page(cache, force)
        
        # Parse
        try:
            tags = page.find('.tag', first = True).find('item')
            tags = {t.text: utils.complete_url(t.attrs['href']) for t in tags}
        
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m tags:', e.args)
        
        self.log.log('Parsed \033[93m{self}\033[0m tags')
        self.tags = tags
        return tags
    
    def get_episodes(self,
                     filter: Callable[[int], bool] = None,
                     cache: bool = True,
                     force: bool = False) -> list[Episode]:
        '''
        Get a list of episodes from the anime.
        --------------------------------------
        
        Arguments
            filter: a function filtering animes numbers.
            cache:  whether to save the fetched data to cache.
            force:  whether to use already cached data.
            
        Returns
            A list of <Episode> objects.
        '''
        
        # Load from cache or fetch
        page = self.get_page(cache, force)
        
        try:
            # Fetch episodes
            objects = page.find('.js-list-episode-container *')
            
            # Parse
            episodes = list({ep.absolute_links.pop()
                            for ep in objects if ep.absolute_links})
            episodes.sort()
            
            # Filter
            filtered = []
            
            if filter is not None:
            
                for ep in episodes:
                    if filter(utils.get_episode_index(ep)):
                        filtered += [Episode(ep, self)]
            else:
                filtered = [Episode(ep, self) for ep in episodes]
        
        except Exception as e:
            self.log.err(f'Failed to get \033[93m{self}\033[91m episodes:', e.args)
        
        self.log.log(f'Parsed {len(filtered)} episodes for \033[93m{self}\033[0m')
        self.episodes = filtered
        return filtered

    def get_episode(self, index: int) -> Episode:
        '''
        Get a special episod.
        This method is faster than calling
        get_episodes, but less stable as urls are
        dynamically generated.
        ------------------------------------------
        
        Arguments
            index: the episode index
        
        Return
            An <Episode> object.
        '''
        
        i = ('-' + str(index).zfill(2) + '_')[::-1]
        ep_url = self.url.replace('/info/', '/episode/')
        
        # Replace last `_` char.
        ep_url = ep_url[::-1].replace('_', i, 1)[::-1]
        
        self.log.log(f'Generated index \033[92m{index}\033[0m url')
        return Episode(ep_url, self)

    def download(self,
                 path: str,
                 pause: int = 5,
                 quality: str | int = consts.Quality.BEST,
                 speed: tuple = consts.Speed.NORMAL,
                 old_method: bool = False) -> list[str]:
        '''
        Download all the episodes from this anime.
        ------------------------------------------
        
        Arguments
            path: the directory path to download to.
            pause: timeout before each episode dl.
            quality: the video quality (constant).
            speed: the download speed (constant).
            old_method: whether to use the old download.
        
        Returns
            A list of paths.
        '''
        
        if not path[-1] in '/\\': path += '/'
        
        pathes = []
        
        for episode in self.get_episodes():
            
            # Download
            ep_path = path + episode.raw_name + '.mp4'
            
            self.log.log(f'Downloading episode \033[93m{episode}\033[0m at \033[92m{ep_path}\033[0m')
            
            params = dict(
                path = ep_path,
                quality = quality,
                ext = False,
                speed = speed
            )
            
            # Download
            if old_method: episode.download_old(**params)
            else: episode.download(speed = speed, **params)
            
            pathes += [ep_path]
            
            # Timeout
            sleep(pause)
        
        return pathes


class Comm:
    def __init__(self,
                 sessions: tuple[req.Session, hreq.HTMLSession] = None,
                 web_cache: str = None) -> None:
        '''
        Represents a scrapping instance.
        --------------------------------
        
        Arguments
            sessions: a sessions tuple for recovering previous sessions.
            web_cache: the location of the web directory for caching.
        '''
        
        # Init sessions
        sessions = sessions or (req.Session(), hreq.HTMLSession())
        self.session, self.html_session = sessions
        
        self.session: req.Session
        self.html_session: hreq.HTMLSession
        
        # Settings
        self.log = log.new_logger('comm')
        self.web_cache = web_cache or './chrome/' # TODO inject to grabber
        
        # self.log.log(f'Initiated new \033[93m{self}\033[0m instance')
    
    def get_dyna(self, url: str) -> hreq.HTMLResponse:
        '''
        Create a request with dynamic html enabled.
        -------------------------------------------
        
        Arguments
            url: The request url to get.
        
        Returns:
            an <HTMLResponse> object (similar to bs4).
        '''
        
        self.log.log(f'Loading page \033[92m{url.split("/")[-1]}\033[0m')
        
        req = self.html_session.get(url)
        req.html.render()
        
        if not req.ok:
            self.log.err('Failed to load page, raised', req.status_code,
                         'with content:', req.content)
        
        return req.html
    
    def get_anime(self, url: str) -> Anime:
        '''
        Fetch an anime from a specific url.
        -----------------------------------
        
        Arguments
            url: the anime url.
        
        Returns
            An <Anime> object.
        '''
        
        return Anime(utils.complete_url(url), self)

# EOF