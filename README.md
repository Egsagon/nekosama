# NS Downloader

Simple utilities to download animes from NS, especially the FHD backend (fusenet).

# Usage

```py

from core import fetcher, scrapper

# Get all NS links to episodes from an anime.
# Return the anime synopsis and a list of urls.
fetcher.get_anime( url: str ) -> tuple[str, list[str]]

# Get the embed url of an anime from its NS url.
fetcher.get_episode( url: str ) -> tuple[str, str]

# Get all the segments url from an embed url.
# Automatically choose the best quality.
fetcher.get_episode_links( url: str ) -> list[str]

# Download an episode given all its segment urls.
fetcher.download_episode( links: list[str], path: str )

# Backend web scrapping function used to get
# all the quality links for an episode embed url.
scrapper.scrap( url: str ) -> str

```

Exemple downloader can be found in `main.py`.

<details>
  <summary>View code</summary>
  
  ```py

import os
from core import fetcher, progress

url = 'Anime url here'
out = './path/to/dir/'

# Create dirs
if not os.path.exists(out): os.makedirs(out)

cla = '\n[ MAIN PY ]'
print(cla, 'Starting')

syn, eps = fetcher.get_anime(url)
open(out + 'syn.txt', 'w').write(syn)

print(cla, 'Wrote syn')

for episode in progress.Bar(cla, eps[7:]):
    
    while 1:
    
        try:
            name = '_'.join(episode.split('/episode/')[1].split('-')[10:])
            
            print(cla, '### Fetching', name)
            
            prov, eurl = fetcher.get_episode(episode)
            links = fetcher.get_episode_links(eurl)
            path = fetcher.download_episode(links, out + name + '.mp4')
            
            print(cla, f'### Fetched {name} ({path = })')
            
            break
    
        except Exception as e:
            print(cla, '\033[91mFailed to scrappe:', e.args, '\033[0m, retrying...')    
        
        except KeyboardInterrupt: print(cla, 'User interruption.')

print(cla, 'Finished process')

  ```
</details>


# Setup

- Install `requirments.txt`
- Install adblocker(s) onto the target browser
