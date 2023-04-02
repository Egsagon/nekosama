'''
Utilities for the core module.
'''

import re
from nekosama import consts

from typing import Callable
from string import ascii_letters, digits


def get_closest_value(iter: list[int], value: int):
    '''
    Pick the closest value in a list.
    From www.entechin.com/find-nearest-value-list-python/
    '''
    
    difference = lambda input_list: abs(input_list - value)
    return min(iter, key = difference)

def select_provider(prov_list: list[str], prov: str) -> str:
    '''
    Select the best provider among all of an episode's providers.
    
    Arguments
        prov_list: list of available providers.
        prov: the desired provider.
    
    Returns the url of the provider.
    '''
    
    assert len(prov_list), 'Could not fetch any provider'
    
    # Use the first of the list, usually the best one
    if prov == consts.provider.BEST:
        return prov_list[0]
    
    # Try to find the provider in the list
    for url in prov_list:
        if prov in url: return url
    
    # Fallback to best if the provider was not found
    return prov_list[0]

def select_quality(qual_list: dict[int, str], qual: str | int) -> str:
    '''
    Select the best quality among all of an episode's provider
    qualities (usually 1080, 720 or 480).
    
    Arguments
        qual_list: list of parsed qualities.
        qual: the desired quality.
        
    Returns the url of the m3u8 file.
    '''
    
    keys = list(qual_list.keys())
    
    match qual:
        
        case consts.quality.BEST:   key = max(keys)
        case consts.quality.WORST:  key = min(keys)
        case consts.quality.HALF:   key = keys[len(keys) // 2]
        
        case ukn:
            if isinstance(qual, int):
                key = get_closest_value(keys, ukn)
            
            else: raise TypeError('Invalid quality', qual)
    
    return qual_list[key]

def parse_qualities(raw: str) -> dict[int, str]:
    '''
    Parse a raw m3u8 list of qualities to a dict.
    format: {quality: m3u8_url}
    
    Arguments
        raw: a string containing the content of the m3u8 file.
    
    Returns a dict linking the qualities to their urls.
    '''
    
    quals = [q.split() for q in re.findall(consts.re.qualities, raw)]
    return {int(''.join(re.findall(r'\d*', q))): u for q, u in quals}

def ghost_format(string: str, **kwargs) -> str:
    '''
    Equivalent of str.format with ghost arguments.
    '''
    
    res = string
    
    for key, value in kwargs.items():
        if '{' + key + '}' in string:            
            res = res.replace('{' + key + '}', str(value))
    
    return res

def get_title(url: str) -> str:
    '''
    Get the title of an anime or episode given its url.
    
    Arguments
        url: the url of the anime or episode
    
    NOTE - Unused.
    '''
    
    raw = re.findall(consts.re.ep_name, url)[0]
    return ' '.join(raw.split('-')).title()

def parse_url(url: str) -> dict[str]:
    '''
    Parse informations from an anime or episode url.
    
    Arguments
        url: the anime or episode url.
    
    Returns a dict were:
        type: the type of the url (anime or episode).
        id: the id of the anime.
        name: the name of the anime.
        lang: VOSTFR or VF.
    '''
    
    infos = re.findall(consts.re.glob_name, url)[0]
    res = {k: v for k, v in zip(['type', 'id', 'name', 'lang'], infos)}
    
    if res['type'] == 'info': res['type'] = 'anime'
    return res

def match_filter(match_: str, filter: str | Callable[[str], bool]) -> bool:
    '''
    Checks whether a filter matches something.
    
    Arguments
        match_: the string to match with.
        filter: the filter to use.
    
    TODO - Add regex filter feature
    '''
    
    if filter is None: return 1
    
    # If filter is a function, pass it the date
    if callable(filter): return filter(match_)
    
    # Format filter
    if '{}' in filter: matches = filter.format(match_)
    else: matches = match_ + filter
    
    return eval(matches)

def normalize(string: str) -> str:
    '''
    Normalize a string for searching.
    
    Arguments
        string: the string to normalize.
    '''
    
    return '' .join([c for c in string.strip()
                     if c in ascii_letters + digits]).lower()

def match_string(match_: str, value: str | re.Pattern) -> bool:
    '''
    Checks whether a string or a regex matches something.
    
    Arguments
        match_: the string to match with.
        value: a string or a regex to check.
    '''
    
    if isinstance(value, re.Pattern):
        return value.match(match_)
    
    a, b = map(normalize, (str(match_), str(value)))
    
    # return (a in b) or (b in a) # not strict enough
    return (a == b) or (b in a)

# EOF