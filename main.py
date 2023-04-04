import time
import nekosama

# Initialise the client
client = nekosama.Client()

# Fetch the anime
anime = client.get_anime('https://neko-sama.fr/anime/info/13532-kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen_vostfr')

def log(status: str, cur: int, total: int | None) -> None:
    
    print([status, cur, total])

start = time.time()

# Download
anime.download(
    'tests/',
    'ff.mp4',
    
    # Settings
    timeout = 0,
    start = 0,
    end = 1,
    
    # Backend arguments
    method = 'safe',
    callback = log,
    quiet = True
)

print('Done in', time.time() - start)

# EOF