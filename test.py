import nekosama

core = nekosama.Core()

anime = core.get('https://neko-sama.fr/anime/info/20596-demon-slayer-hashira-training-arc_vostfr')

ep = anime.episodes[0]

ep.download('test.mp4')

# EOF