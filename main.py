import nekosama as ns

client = ns.Client()

animes = client.search('slime datta ken', lang = 'VOSTFR')

for anime in animes:
    print(anime.name)