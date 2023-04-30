# NEKO SAMA API

An API that scraps the `neko-sama.fr` website.
Is able to search, fetch and download animes.

Supports different video qualities and providers.

License: MIT - See the `LICENSE` file.

# Usage

Simple script to download all the episodes of an anime.
```python
import nekosama as ns

anime = ns.Anime('https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr')

anime.download('slime/', quality = ns.quality.HALF)
```

It can also be used to search for animes on the website.
```python
import nekosama as ns

client = ns.Client()
slimes = client.search('slime datta ken',
                       lang = 'VOSTFR')
```

An example can be found in the `main.py` file.

# Setup

- Use python `3.11` or higher
- Install using pip: `pip install nekosama`
- Optionally, install FFMPEG to your system.

# Docs

A simple documentation is available [here](https://github.com/Egsagon/neko-sama-api/blob/master/doc.md).
For more information, see docstrings and source code.
