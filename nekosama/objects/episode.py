from __future__ import annotations

import base64
from yt_dlp import YoutubeDL
from rich.progress import Progress
from contextlib import nullcontext
from functools import cached_property
from typing import TYPE_CHECKING, Literal, Callable, Type

from .. import consts

if TYPE_CHECKING:
    from .anime import Anime


class NoProgress:
    '''
    Fake tracker that doesn't track progress.
    '''
    
    def add_task(*args, **kwargs): pass
    def update(*args, **kwargs): pass
    
    def __eq__(self, value: object) -> bool:
        return value == Progress

class Episode:
    '''
    Represents an anime episode.
    '''
    
    def __init__(self, anime: Anime, url: str, index: int) -> None:
        '''
        Initialises a new Episode object.
        
        :param anime: Parent anime the episode is issued from.
        :param url: The episode URL.
        :param index: The episode index (1-based).
        '''
        
        self.anime = anime
        self.core = anime.core
        self.url = url
        self.index: int = index
    
    def __repr__(self) -> str:
        return f'Episode({self.anime.slug} {self.anime.lang} - E{self.index})'
    
    @cached_property
    def page(self) -> str:
        '''
        The episode HTML source.
        '''
        
        response = self.core.session.get(self.url)
        response.raise_for_status()
        return response.text
    
    def get_hls(self,
                quality: Literal[1080, 720, 480] = 1080,
                player: int = 0) -> str:
        '''
        Get the HLS playlist URL.
        
        :param quality: The video quality of the source.
        :param player: Player source index to use.
        :return: A valid HLS URL. Will expire after some time.
        '''
        
        html = self.core.session.get(consts.re.players.findall(self.page)[player]).text
        js   = self.core.session.get(consts.re.script.findall(html)[0]).text
        data = base64.b64decode(consts.re.atob.findall(js)[0]).decode()
        hls  = self.core.session.get(consts.re.url.findall(data)[0].replace('\\', '')).text
        return dict(consts.re.qualities.findall(hls))[str(quality)]
    
    def _download(self,
                  path: str,
                  url: str,
                  callback: Callable[[int, int], None],
                  **dl_kw) -> None:
        '''
        Internal download backend.
        
        :param path: The out-tmpl YTDLP arg.
        :param url: the HLS source URL.
        :param callback: Callable for download tracking.
        :param **dl_kw: Additional YTDLP arguments. 
        '''
        
        def hook(data: dict) -> None:
            callback(
                data.get('downloaded_bytes', 0),
                data.get('total_bytes_estimate', 0)
            )
        
        with YoutubeDL({
            'outtmpl': path,
            'progress_hooks': [hook],
            'http_headers': consts.headers,
            'retries': 5,
            'quiet': True,
            'nopart': True,
            'noprogress': True,
            'no_warnings': True
        } | dl_kw) as ytdl:
            ytdl.download([url])
    
    def download(self,
                 path: str,
                 quality: Literal[1080, 720, 480] = 1080,
                 callback: Callable[[int, int], None] = None,
                 tracker: Progress | Type[Progress] | None = Progress,
                 **dl_kw) -> None:
        '''
        Downloads the episode.
        
        :param path: The output file path.
        :param quality: The video source quality.
        :param callback: Callable to track download progress.
        :param tracker: rich progress display for simultaneous downloads.
        :param **dl_kw: Additional YTDLP arguments.
        '''
        
        if tracker is None:
            tracker = NoProgress
        
        with (tracker() if tracker == Progress else nullcontext(tracker)) as progress:
            
            task = progress.add_task(f'E{self.index}')
            
            def wrapper(cur: int, total: int) -> None:
                progress.update(task, completed = cur, total = total)
                if callback: callback(cur, total)
            
            self._download(
                path = path,
                url = self.get_hls(quality),
                callback = wrapper,
                dl_kw = dl_kw
            )

# EOF