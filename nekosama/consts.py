'''
Constants.
'''

class re:
    # Bunch of useful regexes
    
    providers = r"video\[\d\] = '.*';"
    script = r'https://[a-z.]*\/[a-z\/-]*\?.*\" '
    m3u8 = r'\"([a-zA-Z-0-9=]{25,})\"'
    m3u8_urls = r'https.*\"'
    
    qualities = r'NAME=\"\d*\"\nhttps://[^#]*'
    fragments = r'https://.*'
    
    frag_index = r'\d*.ts'

class provider:
    # Providers presets
    BEST = 'best'
    FUSE = 'fusenet'
    PSTREAM = 'pstream'

class quality:
    # Quality presets
    BEST = 'best'
    HALF = 'half'
    WORST = 'worst'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
}