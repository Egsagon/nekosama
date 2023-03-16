import core
from core.consts import Quality

# first call: core.grabber.setup(); exit()

if __name__ == '__main__':
    
    com = core.scrapper.Comm()
    
    anime  = com.get_anime('ns-url-here')
    
    ep = anime.episode[2]
    
    ep.download('test', Quality.MIDDLE)