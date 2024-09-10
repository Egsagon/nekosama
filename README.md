> [!CAUTION]
> This project is discontinuated due to NekoSama going offline. I doubt the website team would ever see this repository, but the website was very nice while it lasted.

# Nekosama

This is a python package for using with the [NekoSama](https://neko-sama.fr/) anime website.
```shell
pip install nekosama
```

## CLI Usage

This package can be used as a CLI tool.

```shell
$ python -m nekosama -h
usage: nekosama [-h] -i INPUT [-e EPISODES] [-o OUTPUT] [-q {1080p,720p,480p}]

options:
  --input INPUT               An anime URL
  --episodes EPISODES         List or range or episodes indexes (e.g. 0-5 or 1,2,3)
  --output OUTPUT             Output directory
  --quality {1080p,720p,480p} Video quality
```

Examples:
```shell
$ nekosama -i <url>          # Download a whole anime
$ nekosama -i <url> -q 480p  # Download in worst quality
$ nekosama -i <url> -e 1     # Download the first episode of an anime
$ nekosama -i <url> -e 1-8   # Download episodes 1 to 8 (included)
$ nekosama -i <url> -e 1,4,9 # Download specific episodes
```

## Package quickstart

```python
import nekosama

# Initialise a core
core = nekosama.Core()

# Search for animes
for anime in core.database.search(query = 'slime'):
    print(anime.title)

# Get an anime from a URL
anime = core.get('https://neko-sama.fr/anime/info/9520-tensei-shitara-slime-datta-ken_vostfr')

# List episodes
for episode in anime.episodes:
    print(episode.index, ':', episode.url)

# Download an episode
anime.episodes[0].download(
    path = 'ep1.mp4',
    quality = 1080
)
```

For more documentation, have a look at the source code and the docstrings.

## License

This project uses the `MIT` license. See the `LICENSE` file for more informations.
