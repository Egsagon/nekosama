import nekosama as ns

anime = ns.Anime('https://neko-sama.fr/anime/info/5944-jormungand_vostfr')

anime.download('jmg/', '{index}.mp4', timeout = 10)

# EOF