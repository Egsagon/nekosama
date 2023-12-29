# NEKO SAMA API

> [!WARNING]
> Dropping support for this. It still works as of late 2023, but you might expect bugs in the future.

An API wrapper for the `neko-sama.fr` anime website. It supports searching and downloading with different
qualities and providers.

# Setup

- Use python `3.11` or higher
- Install using pip: `pip install nekosama`
- Optionally, install FFMPEG to your system.

# Usage

Downloading a whole anime season:
```python
import nekosama as ns

client = ns.Client()
anime = client.get_anime('https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr')

anime.download('slime/', quality = ns.quality.HALF)
```

Downloadnig a single episode:
```python
episode6 = anime.episodes[5]

episode6.download('ep6.mp4', quality = ns.quality.BEST)
```

Searching for animes:
```python
import nekosama as ns

client = ns.Client()
slimes = client.search('slime datta ken',
                       lang = 'VOSTFR')
```

# Docs

A simple documentation is available [here](https://github.com/Egsagon/neko-sama-api/blob/master/doc.md).
For more information, see docstrings and source code.

# License

This project uses the MIT license. See the `LICENSE` file.
