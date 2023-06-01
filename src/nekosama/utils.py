'''
Utilities for the core module.
'''

import re
import os
import subprocess
from nekosama import consts

from typing import Callable


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

def popen(args: list[str], callback: Callable[[str], None]) -> int:
    '''
    Execute a shell command. Each time a line is outputed,
    call the passed callback.
    Returns the returned code.
    '''
    
    proc = subprocess.Popen(
        args,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        text = True
    )
    
    # TODO Refactor
    
    current_line = ''
    
    while True:
        out = proc.stdout.read(1)
        
        if out == '' and proc.poll() != None: break
        
        if out != '':
            if (len(current_line) and \
                current_line[-1] == '\\' and \
                out == 'n' ) or out == '\n':
                
                callback(current_line)
                current_line = ''
            
            current_line += out
            
    return proc.poll()

def fbuild(filter: Callable | str | int | float) -> Callable[[str], bool]:
    '''
    Build a filter.
    '''
    
    # Bypass if already a function
    if callable(filter): return filter
    
    # Always pass if unspecified
    if filter is None: return lambda v: True
    
    # Absolute numbers filter
    if isinstance(filter, int | float):
        return lambda v: float(v) == filter
    
    # Relative evaluations filter
    if isinstance(filter, str):
        
        # Absolute position filter
        if '{}' in filter:
            return lambda v: eval(filter.format(v))
        
        # Left handed filter
        if filter[0] in '<=>':
            return lambda v: eval(v + filter)
        
        # Right handed filter
        if filter[-1] in '<=>':
            return lambda v: eval(filter + v)
    
    raise TypeError('Invalid filter:', filter)

# EOF