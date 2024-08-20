import httpx
from . import consts
from .objects.anime import Anime
from .objects.database import Database

class Core:
    '''Represents a single connection to the target website.'''
    
    def __init__(self, client: httpx.Client = None) -> None:
        '''Initialises a new Core object.'''
        
        self.session = client or httpx.Client(
            headers = consts.headers,
            follow_redirects = True
        )
        
        self.database = Database(self)
    
    def get(self, url: str) -> Anime:
        '''Get an anime or episode.'''
        
        return Anime(self, url)

# EOF