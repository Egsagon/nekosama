from __future__ import annotations

import os
from concurrent import futures
from rich.progress import Progress
from functools import cached_property
from typing import TYPE_CHECKING, Literal, TypedDict

from .. import consts
from .episode import Episode

if TYPE_CHECKING:
    from ..core import Core


class AnimeData(TypedDict):
    title: str
    type: str
    url: str
    image: str
    description: str


class Anime:
    '''
    Represents an anime.
    '''
    
    def __init__(self, core: Core, url: str) -> None:
        '''
        Initialises a new Anime object.
        
        :param core: Nekosama core to use.
        :param url: Anime URL.
        '''
        
        self.core = core
        self.url = url.lower()
        
        url_data = consts.re.url_data.match(self.url).groups()
        self.id = int(url_data[0])
        self.slug: str = url_data[1]
        self.lang: Literal['VO', 'VF'] = url_data[2][:2].upper()
        
    def __repr__(self) -> str:
        return f'Anime({self.slug} {self.lang})'
    
    @cached_property
    def page(self) -> str:
        '''
        The anime HTML source.
        '''

        response = self.core.session.get(self.url)
        response.raise_for_status()
        return response.text
    
    @cached_property
    def data(self) -> AnimeData:
        '''
        The anime data.
        '''
        
        return dict(consts.re.anime_data.findall(self.page))
    
    @cached_property
    def title(self) -> str:
        '''
        The anime title.
        '''
        
        return self.data['title'].split('|')[0].strip()
    
    def get_image(self) -> bytes:
        '''
        Get the anime poster.
        
        :return: The raw image bytes.
        '''
        
        response = self.core.session.get(self.data['image'])
        response.raise_for_status()
        return response.content
    
    @cached_property
    def episodes(self) -> list[Episode]:
        '''
        Anime episodes.
        '''
        
        urls = consts.re.episodes.findall(self.page)
        return [Episode(self, url, i) for i, url in enumerate(urls, start = 1)]

    def download(self,
                 path: str,
                 quality: Literal[1080, 720, 480] = 1080,
                 workers: int = 1) -> None:
        '''
        Downloads the whole anime.
        
        :param path: Parent directory for all downloads.
        :param quality: Download quality.
        :param workers: Amount of concurent download workers.
        '''
        
        os.makedirs(path, exist_ok = True)
        
        with Progress() as progress, futures.ThreadPoolExecutor(workers) as pool:
            
            threads = [
                pool.submit(
                    episode.download,
                    path = os.path.join(path, f'{episode.index}.mp4'),
                    quality = quality,
                    tracker = progress
                )
                for episode in self.episodes
            ]
            
            
            for thread in threads:
                if thread.cancelled():
                    continue
                
                try:
                    thread.result()
                
                except KeyboardInterrupt:
                    pool.shutdown(wait = False, cancel_futures = True)
                    raise

# EOF