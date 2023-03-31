import re
import consts

def get_closest_value(iter: list[int], value: int):
    '''
    Pick the closest value in a list.
    From www.entechin.com/find-nearest-value-list-python/
    ---------------------------------
    '''
    
    difference = lambda input_list: abs(input_list - value)
    
    res = min(iter, key = difference)
    
    return res

def select_provider(prov_list: list[str], prov: str) -> str:
    '''
    Select the best provider among all of an episode's providers.
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

# EOF