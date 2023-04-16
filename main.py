import nekosama
from time import time, sleep
import tkinter.filedialog as file

client = nekosama.Client()

query = input('> Enter query or URL: ')

if not 'https://' in query:
    
    animes = client.search(query, limit = 10)
    
    print(f'Found {len(animes)} animes for \033[92m{query}\033[0m:')
    
    for i, a in enumerate(animes):
        print(f'\t* {i}. {a.name}')
    
    index = int(input('> Select index (default=0): ') or 0)
    
    anime = animes[index]

else:
    anime = client.get_anime(query)

print(f'Selected anime: \033[92m{anime.title}\033[0m')

start = int(input('> Set range start (default=0): ') or 0)
end = eval(input('> Set range end (default=-1): ') or 'None')

episodes = anime.episodes[start:end]

path = input('> Set path (default=tkinter): ') or file.askdirectory()

assert path

if not path[-1] in '/\\': path += '/'

timeout = int(input('> Set request timeout (default=5): ') or 5)

backend = input('Set backend (default=ffmpeg): ') or 'ffmpeg'

print(f'Downloading {len(episodes)} episodes:')

for i, ep in enumerate(episodes):
    print(f'\t* {i}. {ep.name}')

input('> Download ready. Press enter to continue. ')

print('\n\033[92m=> Starting download!\033[0m')

global_start_time = time()
times = []
times_wtm = []

def debug(status, current, total) -> None:
    # Debug backend callable
    
    print(f'\r\t\033[93m?\033[0m {status} [{current} / {total}]', end = '')

for episode in episodes:
    
    episode_start_time = time()
    
    print('\n* Downloading', episode.index)
    
    episode.download(path + str(episode.index) + '.mp4',
                     method = backend, callback = debug, quiet = True)
    
    times += [time() - episode_start_time]
    sleep(timeout)
    times_wtm += [time() - episode_start_time]


global_time = time() - global_start_time

print('\033[92m\nDownloaded all episodes!\033[0m')

print(f'Downloaded {len(episodes)} in {round(global_time, 2)}s.')
print(f'Average download speed: {round(sum(times) / len(times)), 2}s.')
print(f'Average speed with timeouts: {round(sum(times_wtm) / len(times_wtm), 2)}s.')

print('Times:')

for i, t in enumerate(times):
    print(f'\t* {i}. {round(t, 2)}s')
    
print('Exiting.')
