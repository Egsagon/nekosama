from re import compile


headers = {
    'Accept': '*/*',
    'Accept-Language': 'en,en-US',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
}

class re:
    '''Collection of internal regexes.'''
    
    anime_data = compile(r'<meta property=\"og:(?P<name>.*)\" content=\"([.\s\S]*?)\" />')
    url_data   = compile(r'https://.*?/(\d*)-([a-z-\d]*)_(vostfr|vf)')
    episodes   = compile(r'https://neko-sama\.fr/anime/episode/\d*[a-z-\d_]*')
    players    = compile(r"video\[\d\] = '(.*?)';")
    script     = compile(r'https://[a-z.]*\/[a-z\/-]*\?.*\" ')
    atob       = compile(r'atob\(\"(.*?)\"\)')
    url        = compile(r'(https.*?)\"')
    qualities  = compile(r'=\"(\d+?)\"\n(http.*?)(?:\n|$)')
    
# EOF