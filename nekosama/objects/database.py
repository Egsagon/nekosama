from __future__ import annotations

from .. import consts
from .anime import Anime

from functools import cached_property
from typing import TYPE_CHECKING, Iterator, Literal, Callable

if TYPE_CHECKING:
    from ..core import Core


class Database:
    '''
    Represents the website database.
    '''
    
    def __init__(self, core: Core) -> None:
        '''
        Initialise a new database instance.
        
        :param core: Nekosama core to use. 
        '''
        
        self.core = core
    
    def _fetch(self, url: str) -> list[dict]:
        '''
        Shorthand for fetching a JSON ressource.
        
        :param url: Ressource URL to fetch.
        :return: The parsed ressource.
        '''
        
        response = self.core.session.get(url)
        response.raise_for_status()
        return response.json()
    
    @cached_property
    def VO(self) -> list[dict]:
        return self._fetch('https://neko-sama.fr/animes-search-vostfr.json')
    
    @cached_property
    def VF(self) -> list[dict]:
        return self._fetch('https://neko-sama.fr/animes-search-vf.json')
    
    def search(self,
               query: str = None,
               lang: Literal['VO', 'VF'] = 'VO',
               type: consts.Type = None,
               genres: set[consts.Genre] = None,
               custom: Callable[[dict], bool] = None) -> Iterator[Anime]:
        '''
        Search for animes in the database.
        
        :param query: Keywords to search for.
        :param lang: Database language.
        :param type: Specific anime type.
        :param genres: Specific anime genres.
        :param custom: A custom filter callable.
        :return: An Anime iterator.
        '''
        
        def callback(data: dict) -> bool | None:
            
            if custom and not custom(data):                           return False
            if type   and type != data['type']:                       return False
            if genres and not genres.issubset(data['genres']):        return False
            if query  and query.lower() not in data['title'].lower(): return False
            
            return True
        
        for data in filter(callback, getattr(self, lang)):
            yield Anime(self.core, data['url'])

# EOF