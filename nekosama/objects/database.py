from __future__ import annotations
from .. import consts
from functools import cached_property
from typing import TYPE_CHECKING, TypedDict, Iterator


if TYPE_CHECKING:
    from ..core import Core

class Data(TypedDict):
    id: int
    title: str
    others: str
    type: str
    status: str
    popularity: float
    url: str
    genres: list[str]
    url_image: str
    score: str
    start_date_year: str
    nb_eps: str


class Database:
    '''Represents the website database.'''
    
    def __init__(self, core: Core) -> None:
        '''Initialise a new database instance.'''
        
        self.core = core
    
    def _fetch(self, url: str) -> list[dict]:
        '''Shorthand for fetching a JSON ressource.'''
        
        response = self.core.session.get(url)
        response.raise_for_status()
        return response.json()
    
    @cached_property
    def VO(self) -> list[dict]:
        '''The '''
        
        return self._fetch('https://neko-sama.fr/animes-search-vostfr.json')
    
    @cached_property
    def VF(self) -> list[dict]:
        ''' ... '''
        
        return self._fetch('https://neko-sama.fr/animes-search-vf.json')
    
    @cached_property
    def ALL(self) -> list[dict]:
        ''' ... '''
        
        return self.VO + self.VF
    
    def search(self) -> Iterator[object]:
        pass

# EOF