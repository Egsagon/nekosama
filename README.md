# NS Downloader

Simple utilities to download animes from NS, especially the FHD backend (fusenet).

Note: theorically the other backend (pstream, SD) works same, but fusenet is default
and provide more quality (ig).

# Usage

```py

import core
from core.consts import Quality

# Initialise the communication instance
com = core.scrapper.Comm()

# Fetch an anime
anime  = com.get_anime('enter-ns-url-here')

# Get an episode
ep = anime.episode[2]

# Download the episode
ep.download('episode_2', Quality.MIDDLE)

```

An API example can be found in `main.py`, and an example ui can be found in `ui.py`:

![demo](https://github.com/Egsagon/NS-API/blob/master/src/demo.png)



# Setup

- Install `requirments.txt` using pip
- Run the browser at blank:

```py
import core
core.grabber.setup()
```
- Use it to install adblocker(s) (like `ublock origin`).

# Structure

## Comm
The `Comm` object is an instance that centralize the sessions
for all requests.
Useful methods:

- `get_anime( url: str ) -> Anime`: Associate an `Anime` object for an url.

## Anime
The `Anime` object contains methods about getting anime data and episodes.

- `get_synopsis() -> str`: Get the raw anime' synopsis.
- `get_data() -> dict[str, str]`: Get useful informations about the anime (rating, type, etc.)
- `get_picture() -> Image`: Get the anime' presentation picture.
- `get_poster() -> Image`: Get the anime' presentation poster (background image).
- `get_tags() -> dict[str, str]`: Get the anime' search tags and their url.

- `get_episode( index: int )`: Get one specific episode of the anime.
- `get_episodes() -> list[episodes]`: Get ALL the anime episodes.

- `download( path: str, pause: int, quality: int | str | constant) -> list[str]`: Download all the episodes from the anime, given a certain directory and quality.

Most of those functions use a caching system. When they do, you can override the cache
by specifying the `force: bool` argument to refresh the request, and the ``cache: bool`
argument to avoid (re)writing to the cache.

Those functions also have an equivalent attribute which will call them when called.
E.g:
```py
s = anime.get_synopsis()
# is same as
s = anime.synopsis
# if no argument to specify are needed.
```

Moreover, the `episode` (no 's') argument will call a generator-like object that allows
for parsing only one episode at a time.

## Episode
The `Episode` object if provided by an `Anime` objects and is a representation of an episode of this anime. It can also be initiated using the classmethod `from_url`, but you also need to provide a `Comm` instance to it.

- `get_picture() -> Image`: Same as `Anime`.
- ``download( path: str, quality: str, ext: bool) -> str`: Download the episode at a certain path with (or not) an extension and with a specific quality.

### Note: Specifiying quality
Quality can either be:
- an `int`, referencing a video quality (1080, 720, etc). Will be picked the nearest possible value to it.
- an `str`, either `best`, `worst`, or `middle`.

- a constant of `core.consts.Quality`, essentially the same as `str`.

## Image
The `Image` object is created by both `Anime` and `Episode` objects.
It contains the following attributes: url, ext(ension), url and has one method:
- `download( path: str, ext: bool )`: Download the image to a path, with (or not) an extension.
