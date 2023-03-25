import core
from time import time

if __name__ == '__main__':
    
    com = core.scrapper.Comm()
    anime  = com.get_anime('https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr')
    ep = anime.episode[10]
    
    start = time()
    
    ep.download('ep10')
    
    print('\nDone in', time() - start)

'''
VANILLA - 183s
THREADS - 51s
'''

# EOF