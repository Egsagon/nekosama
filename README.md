# neko-sama-api

An API that scraps the `neko-sama.fr` website.
Is able to search, fetch and download animes.

Supports different video qualities and providers.

License: MIT - See the `LICENSE` file.

# Usage

Simple script to download all the episodes of an anime:
```python
import nekosama as ns

anime = ns.Anime('https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr')

anime.download('slime/', quality = ns.quality.HALF)
```

It can also be used to search for animes on the website:
```python
import nekosama as ns

client = ns.Client()
slimes = client.search('slime datta ken',
                       lang = 'VOSTFR')
```

An example can be found in the `main.py` file,
and a ui in the `ui.py` file.

# Setup

- Install the python ackages:
    - `requests`,
    - `pytyhon-ffmpeg`

- Clone the repository:
```sh
git clone https://github.com/Egsagon/neko-sama-api
cd neko-sama-api/
python3 main.py
```

# Docs

## Client
The client object handles searching animes.
It generates `Anime` objects. It is also
responsible for keeping the same requests
session between all animes and episodes instances.

```python
# Initialisation
>>> client = ns.Client()

# Get an anime from a url
>>> client.get_anime('https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr')
<Anime `tensei-shitara-slime-datta-ken`>

# Search animes on the website
>>> client.search('slime datta ken', lang = 'VOSTFR')
[<Anime `tensei-shitara-slime-datta-ken`>, <Anime `tensei-shitara-slime-datta-ken-2nd-season-part-2`>, <Anime `tensei-shitara-slime-datta-ken-2nd-season`>, <Anime `tensura-nikki-tensei-shitara-slime-datta-ken`>, <Anime `tensei-shitara-slime-datta-ken-kanwa-verudora-nikki`>]
```

The `search` function can be filtered with multiple other arguments (name, genres, date, score, and more).

## Anime
The Anime object represents an anime on the platform.
It handles fetching anime data and episodes. It can be initialized in two ways:
from the `Client.get_anime` method or with a specifif url:

```python
>>> anime = ns.Anime('https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr')
>>> anime.title
Tensei Shitara Slime Datta Ken VOSTFR | Neko-sama
>>> anime.description
Aucun synopsis pour le moment.
```

It has the following methods:
```python
# Download the anime poster
anime.download_image('image.jpg')

# Download the anime background picture
anime.download_background('image.jpg')

# Download all the episodes to dir
anime.download('dir/')
```

The `anime.download` method has multiple other parameters,
such has using a specific name formating, quality or provider. See its docstring for reference.

The object also has multiple properties, like `title`, `tags`, `description`, or `episodes`.

###### Note `Anime.name` is the raw name used for path naming, while `Anime.title` is the fancy name

The episode objects returns a list of `Episode` objects.

## Episode
They represent one episode of an anime.

Available properties:
```python
episode = anime.episodes[0]
episode.time  # Episode duration in minutes
episode.title # Fancy title of the episode
episode.index # Index in the episodes list
```

Available methods:
```python
episode.download_image() # Download the episode poster
episode.download('ep_1.mp4') # Download the episode
```

The `episode.download` method has multiple other parameters,
such has using a specific path formating, quality or provider. See its docstring for reference.


# TODO

- Logging
- UI example
- Refactor regexes