import core
from core.consts import Quality

# first call: core.grabber.setup()

if __name__ == '__main__':
    
    url = 'https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr'
    
    com = core.scrapper.Comm()
    
    anime  = com.get_anime(url)
    
    ep = anime.episode[2]
    
    ep.download('test', Quality.MIDDLE)