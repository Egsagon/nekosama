'''
    Nekosama 4.0
    
    See https://github.com/Egsagon/neko-sama-api.
'''

from .core import Core
from . import consts

from .objects.anime import Anime
from .objects.episode import Episode
from .consts import Type, Genre

from rich.progress import Progress

__all__ = ['Core', 'consts', 'Anime', 'Episode', 'Type', 'Genre']

# EOF