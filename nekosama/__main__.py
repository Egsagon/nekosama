import os
import argparse

from nekosama import Core


header = '\x1b[2m( NEKO )\x1b[0m'

parser = argparse.ArgumentParser(
    prog = 'nekosama',
    description = 'Download CLI for nekosama.fr\nSee https://github.com/Egsagon/neko-sama-api for help.'
)

def error(message: str) -> None:
    print(header, f'\x1b[91m{message}\x1b[0m')
    exit()

parser.error = error

parser.add_argument(
    '-i', '--input',
    help = 'An anime URL',
    required = True
)

parser.add_argument(
    '-e', '--episodes',
    help = 'List or range or episodes indexes (e.g. 0-5 or 1,2,3)',
    default = '0-'
)

parser.add_argument(
    '-o', '--output',
    help = 'Output directory',
    default = '.'
)

parser.add_argument(
    '-q', '--quality',
    help = 'Video quality',
    default = '1080p',
    choices = ['1080p', '720p', '480p']
)

args = parser.parse_args()

# Get anime
core = Core()
anime = core.get(args.input)

print(header, f'Fetched anime \x1b[92m{anime.title}\x1b[0m')

# Get episode range
if ',' in args.episodes:
    indexes = list(map(int, args.episodes.split(',')))

elif '-' in args.episodes:    
    start, stop = args.episodes.split('-')    
    indexes = range(int(start or 0), int(stop or -1) + 1)

else:
    indexes = [int(args.episodes)]

episodes = [ep for ep in anime.episodes if ep.index in indexes]

if not episodes:
    error('No episode found matching query')

print(header, f'Downloading \x1b[92m{len(episodes)}\x1b[0m episodes.')

try:
    for episode in episodes:
        episode.download(
            path = os.path.join(args.output, f'{episode.anime.slug}-ep{episode.index}'),
            quality = int(args.quality.replace('p', ''))
        )

except KeyboardInterrupt:
    error('Canceled by user')

except Exception as err:
    error(repr(err))

print(header, 'Success!')

# EOF