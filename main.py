import core
from time import time

if __name__ == '__main__':
    
    com = core.scrapper.Comm()
    anime  = com.get_anime('ns-url-here')
    pathes = anime.download('dir/')
    
    print('\n\n\n', pathes)

# EOF