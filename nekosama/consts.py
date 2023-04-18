'''
Constants for the core module.
'''

root = 'https://neko-sama.fr'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
}

class re:
    '''
    Useful parsing regexes.
    TODO refactor names
    '''
    
    ep_list    = r'var episodes = ([^;]*)'                              # Get eps list
    providers  = r"video\[\d\] = '.*';"                                 # Get ep providers
    script     = r'https://[a-z.]*\/[a-z\/-]*\?.*\" '                   # Get backend script
    m3u8       = r'\"([a-zA-Z-0-9=]{25,})\"'                            # Get M3U8 info
    m3u8_urls  = r'https.*\"'                                           # Get M3U8 urls
    qualities  = r'NAME=\"\d*\"\nhttps://[^#]*'                         # Get quality urls
    fragments  = r'https://.*'                                          # Get fragment urls
    ep_id      = r'https://.*/episode/(\d*)'                            # Get episode id
    ep_index   = r'https:\/\/.*\/episode\/.*-(\d*)_.*'                  # Get episode index
    ep_name    = r'https:\/\/.*\/episode\/\d*-(.*)_'                    # Get episode name
    valid_ep   = r'https://neko-sama\.fr/anime/episode/\d*[a-z-\d_]*'   # Validate an episode
    frag_index = r'\/(\d*)\.ts'                                         # Get fragment index
    ani_tags   = r'&quot;(.*?)&quot;'                                   # Get anime search tags
    an_from_ep = r'href=\"(/anime/info/.*)\" class=\"cover\"'           # Get ani url from ep page
    ep_bg      = r'\"head\" style=\"background-image: url\((https://.*)\)' # Get ep bg image url
    
    glob_name  = r'https://.*/anime/(info|episode)/(\d*)-([a-z-\d]*)_(vostfr|vf)' # Get url data
    ani_props  = r'<meta property=\"og:(?P<name>.*)\" content=\"([.\s\S]*?)\" />' # Get meta props
    

class provider:
    '''
    Representations of providers.
    Possible values: BEST, FUSE, PSTREAM.
    '''
    
    BEST = 'best'
    FUSE = 'fusenet'
    PSTREAM = 'pstream'

class quality:
    '''
    Quality presets. Can also
    be an int instead.
    '''
    
    BEST = 'best'
    HALF = 'half'
    WORST = 'worst'

class genre:
    thriller = 'thriller'
    fantasy = 'fantasy'
    hentai = 'hentai'
    mystery = 'mystery'
    ecchi = 'ecchi'
    mahou_shoujo = 'mahou shoujo'
    shoujo = 'shoujo'
    adventure = 'adventure'
    romance = 'romance'
    shounen = 'shounen'
    slice_of_life = 'slice of life'
    horror = 'horror'
    sports = 'sports'
    isekai = 'isekai'
    magic = 'magic'
    mafia = 'mafia'
    military = 'military'
    yuri = 'yuri'
    mecha = 'mecha'
    psychological = 'psychological'
    drama = 'drama'
    cyberpunk = 'cyberpunk'
    music = 'music'
    action = 'action'
    sci_fi = 'sci-fi'
    battle_royale = 'battle royale'
    supernatural = 'supernatural'
    comedy = 'c0m1d'

class type:
    tv = 'tv'
    ova = 'ova'
    movie = 'm0v1e'
    special = 'special'
    
    unknown = ''

# EOF