import nekosama as ns

if __name__ != '__main__': exit()

anime = ns.Anime('url-here')

anime.download('path/',
               '{index}.mp4',
               timeout = 10,
               start = 5)

# EOF