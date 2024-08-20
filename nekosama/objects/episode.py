from __future__ import annotations
import base64
from .. import consts
from yt_dlp import YoutubeDL
from rich.progress import Progress
from functools import cached_property
from contextlib import contextmanager
from typing import TYPE_CHECKING, Literal, Callable, ContextManager

if TYPE_CHECKING:
    from .anime import Anime


@contextmanager
def default(desc: str = '') -> object:
    with Progress() as track:
        task = track.add_task(desc)
        
        def wrapper(a: int, b: int) -> None:
            track.update(task, completed = (a / b) * 100)
        
        yield wrapper


class Episode:
    '''Represents an anime episode.'''
    
    def __init__(self, anime: Anime, url: str, index: int) -> None:
        '''Initialises a new Episode object.'''
        
        self.anime = anime
        self.core = anime.core
        self.url = url
        self.index: int = index
    
    def __repr__(self) -> str:
        return f'Episode({self.anime.slug} {self.anime.lang} - E{self.index})'
    
    @cached_property
    def page(self) -> str:
        '''The episode HTML source.'''
        
        response = self.core.session.get(self.url)
        response.raise_for_status()
        return response.text
    
    def get_hls(self,
                quality: Literal[1080, 720, 480] = 1080,
                player: int = 0) -> str:
        '''Get the HLS playlist URL.'''
        
        html = self.core.session.get(consts.re.players.findall(self.page)[player]).text
        js   = self.core.session.get(consts.re.script.findall(html)[0]).text
        data = base64.b64decode(consts.re.atob.findall(js)[0]).decode()
        hls  = self.core.session.get(consts.re.url.findall(data)[0].replace('\\', '')).text
        return dict(consts.re.qualities.findall(hls))[str(quality)]
    
    def download(self,
                 path: str,
                 quality: Literal[1080, 720, 480] = 1080,
                 player: int = 0,
                 manager: ContextManager[Callable[[int, int], None]] = default,
                 **dl_kw) -> None:
        '''Download the episode.'''
        
        url = self.get_hls(quality, player)
        
        with manager() as track:
            def hook(data: dict) -> None:
                track(
                    data.get('downloaded_bytes', 0),
                    data.get('total_bytes_estimate', 0)
                )
            
            with YoutubeDL({
                'outtmpl': path,
                'progress_hooks': [hook],
                'http_headers': consts.headers,
                'retries': 5,
                'quiet': True,
                'noprogress': True,
                'no_warnings': True
            } | dl_kw) as ytdl:
                ytdl.download([url])

# EOF