import nekosama

# Initialise the client
client = nekosama.Client()

# Fetch the anime
anime = client.get_anime('https://neko-sama.fr/anime/info/13532-kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen_vostfr')

def log(cur: str) -> None:
    print('\r     * Downloading', cur, end = '')

# Download
anime.download(
    'liw/',
    '{index}.mp4',
    
    # Settings
    timeout = 10,
    start = 0,
    
    # Backend arguments
    method = 'thread_ffmpeg',
    callback = log,
    quiet = True
)

# EOF