'''
    A bunch of constants and errors classes.
'''

segments_headers = {
    'Host': 'fusevideo.net',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
}

class Quality:
    BEST = 'best'
    WORST = 'worst'
    MIDDLE = 'middle'

class Speed:
    # Defaut
    NORMAL      = None      # Leads to SAFE, download in avg 50s
    
    # Normal queues
    ULTRASAFE   = (.1, 1)   # 1x10 req/s | Won't overload the target
    SAFE        = (.05, 1)  # 1x2 req/s  | Most likely target rate limit
    FAST        = (.03, 1)  # 1x-- req/s | More fails, not really rentable
    ULTRAFAST   = (.01, 1)  # 1x10 req/s | Same as fast but even more fails
    
    # Chunks
    SAFECHUNK   = (.05, 4)  # 4x2 req/s  | Send requests by chunks of n
    FASTCHUNK   = (.05, 8)  # 8x2 req/s  | Same as SAFECHUNK
    
    # Experimental
    GASGASGAS   = (0, 0)    # inf req/s  | doesn't wait at all

# Errors

class FetchingErorr(Exception): pass

class NotMyFaultError(Exception): pass