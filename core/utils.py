import re
from tqdm import tqdm


# URL manipulation functions

def parse_name(url: str, uid: bool = False) -> str:
    '''
    Get an anime name from its url.
    -------------------------------
    
    Arguments
        url: the anime url
        uid: wheter to keep the anime id.
    
    Returns
        A parsed name string.
    '''
    
    raw = url.split('/')[-1]
    
    # With id
    if uid: return raw
    
    # Without id
    else: return re.sub(r'\d{1,6}-', '', raw)

def format_name(name: str) -> str:
    '''
    Format an url name to appropriate case.
    ---------------------------------------
    
    Arguments
        name: the name.
    
    Returns
        A formated name.
    '''
    
    res = re.sub(r'[-_]', ' ', name, flags = re.M).title()
    res = re.sub(r'vostfr', 'VOSTFR', res, flags = re.I)
    
    return res

def complete_url(url: str) -> str:
    '''
    Autocomplete an url if the root is missing.
    -------------------------------------------
    
    Arguments
        url: the anime url.
    
    Returns
        a complete url.
    '''
    
    '''
    domain = 'neko-sama.fr'
    root = 'https://neko-sama.fr/anime/'
    
    root_gl = 'info/'
    root_ep = 'episode/'
    
    name = parse_name(url, uid = False)
    
    # Decide whether url is an episode or global info
    is_ep = re.match(r'\d{1,3}_', url)
    sup = root_ep if is_ep else root_gl
    
    # Full URL
    if root + sup in url: return url
    
    # URL missing sup (and therefore root else invalid)
    if not sup in url:
        
        # Check that id is present
        if not (uid := url.split('-')[0].split('/')[-1]).isdecimal():
            raise Exception(f'Invalid URL: {url} ({uid})')
        
        # Remove leading slash
        if url[0] == '/': url = url[1:]
        return root + sup + url
    
    # URL missing root
    if not root in url:
        
        # Remove leading slash
        if url[0] == '/': url = url[1:]
        return root + url
    
    # URL missing protocol
    if domain in url:
        if url.startswith('/' + domain):
            return 'https:/' + url
        
        return 'https://' + url
    
    raise Exception(f'Invalid URL: {url}')
    '''
    
    proto = 'https://'
    domain = 'neko-sama.fr'
    root = proto + domain
    
    # TODO refactor
    
    if proto in url: return url
    
    if domain in url:
        return proto + url
    
    if '/anime/' in url:
        return root + url
    
    if 'anime/' in url:
        return root + '/' + url
    
    raise Exception('Unparsable URL:', url)

def get_extension(url: str) -> str:
    '''
    Get the extension of a media accessed through an url.
    '''
    
    matches = re.findall(r'\.[a-z]{3}', url)
    
    return matches[-1].replace('.', '')

def get_anime_from_episode_url(url: str) -> str:
    '''
    Get the anime URL given an episode URL.
    ---------------------------------------
    
    Argument
        url: the anime url.
    
    Returns
        An anime url string.
    '''
    
    return re.sub(r'-\d{1,3}_', '_', url).replace('/episode/', '/info/')

def get_episode_index(url: str) -> int:
    '''
    Return an episode index given its url.
    '''
    
    raw = re.findall(r'-\d+_', url)
    
    if len(raw) != 1: raise Exception('Could not parse episode url:', url)
    
    return int(re.sub(r'[-_]', '', raw[0], flags = re.M))


# Parsing functions

def get_closest_value(iter: list[int], value: int):
    '''
    Pick the closest value in a list.
    From www.entechin.com/find-nearest-value-list-python/
    ---------------------------------
    '''
    
    difference = lambda input_list: abs(input_list - value)
    
    res = min(iter, key = difference)
    
    return res

def parse_qualities(raw: str, quality: str | int) -> str:
    '''
    Parse the output of grabber.grab_request into a list
    of disponible qualities and choose the best one
    compared to the quality argument.
    
    Arguments
        raw: the output of the grabber
        quality: See scrapper.Episode.download docstring.
    '''
    
    qual = [l.split('\n')[:-1] for l in '\n'.join(raw.split('\n')[1:]).split('#')[1:]]
    quals = {int(data.split('=')[-1].replace('"', '')): link for data, link in qual}
    
    keys = list(quals.keys())
    
    key = None
    
    if isinstance(quality, int):
        # Pick nearest
        
        key = get_closest_value(keys, quality)
    
    else:
        match quality:
            # Best quality possible
            case 'best': key = max(keys)
            
            # Lowest quality possible
            case 'worst': key = min(keys)
            
            # In-middle quality
            case 'middle': key = keys[len(keys) // 2]
    
    # Return the url
    return quals[key]

# Logging functions

def bar(msg: str, iter: list, show: bool = True) -> tqdm:
    '''
    TQDM bar wrapper.
    -----------------
    
    Arguments
        msg: message to be displayed along the bar.
        iter: the list to generator through.
        switch: logging toggle.
    
    Returns
        A TQDM generator.
    '''
    
    if not show: return iter
    
    return tqdm(iter,
                bar_format = '{desc} ╞{bar}╡ {n_fmt}/{total_fmt} ({percentage:3.0f}%)',
                ascii = ' ═',
                desc = msg)

# EOF