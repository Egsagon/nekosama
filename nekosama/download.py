'''
List of backends used by the 
core module to download animes.
'''

import os
import re
import time
import copy

import ffmpeg
import requests
import threading

from typing import Callable

from nekosama import consts

BACKENDS = [
    'ffmpeg',
    'thread',
    'thread_ffmpeg',
    'safe'
]

def reach(method: str) -> Callable:
    '''
    Reach a backend function.
    '''
    
    if not method in BACKENDS:
        raise Exception('Invalid backend', method)
    
    return eval('bk_' + method)


def bk_ffmpeg(raw: str,
              path: str,
              **kwargs) -> None:
    '''
    Download using the ffmpeg download feature.
    '''

    # Write the m3u8 file for ffmpeg
    with open('temp.m3u', 'w') as file:
        file.write(raw)
    
    # Send the ffmpeg command    
    ffmpeg.input(
        'temp.m3u',
        protocol_whitelist = 'file,http,https,tcp,tls,crypto'
    
    ).output(path, acodec = 'copy', vcodec = 'copy'
    ).run(overwrite_output = True)
    
    # Delete the temp file
    os.remove('temp.m3u')
    
    return

def dl_frag(req: requests.PreparedRequest,
            timeout: float,
            session: requests.Session,
            data: dict = None,
            todo: list = None) -> bytes | None:
    '''
    Download a single fragment.
    '''
    
    raw = session.send(req).content
    
    while b'<html>' in raw:
        
        # If request fails, put it back in todo
        if todo is not None:
            return todo.append(req)
        
        time.sleep(timeout)
        raw = session.send(req).content
    
    else:
        if data is None: return raw
        key = int(re.findall(consts.re.frag_index, req.url)[0])
        data[key] = raw

def bk_base_thread(raw: str,
                   timeout: float = .05,
                   **kwargs) -> dict[int, bytes]:
    '''
    Download each fragment using threads.
    Theorically faster.
    Instead of writing it to a path, returns it.
    '''
    
    chunks = re.findall(consts.re.fragments, raw)
    reqs = [requests.Request('GET', chunk, consts.headers).prepare() for chunk in chunks]
    session = requests.session()
    
    data = {}
    todo = copy.deepcopy(reqs)
    
    while len(todo):
        current = todo.pop(0)
        
        t = threading.Thread(
            target = dl_frag,
            args = [current, timeout, session, data, todo]
        )
        
        t.start()
        
        time.sleep(timeout)
        
        # Debug
        print('*', len(data), len(todo))
    
    # Check for missing chunks
    for i in range(len(chunks)):
        if not i in data.keys():
            
            # Debug
            print('Downloading missing', i)
            
            # Get chunk request
            mreq = [r for r in reqs if r.url.endswith(f'{i}.ts')][0]
            data[i] = dl_frag(mreq, timeout, session)
    
    return data

def bk_thread(raw: str,
              path: str,
              timeout: float = .05,
              **kwargs) -> None:
    '''
    Download each fragment using threads.
    Theorically faster.
    '''
    
    # Fetch the chunks
    chunks = bk_base_thread(raw, timeout)
    
    # Write them to the file
    with open(path, 'wb') as output:
        for key in sorted(chunks.keys()):
            print('Writing', key)
            output.write(chunks[key])
    
    return
    
def bk_thread_ffmpeg(raw: str,
                     path: str,
                     timeout: float = .05,
                     **kwargs) -> None:
    '''
    Same as thread, but uses ffmpeg to concatenate.
    '''
    
    # Fetch the chunks
    chunks = bk_base_thread(raw, timeout)
    
    temp = './temp/'
    track = ''
    
    # Create temp folder if needed
    if not os.path.exists(temp): os.mkdir(temp)
    
    for index, chunk in chunks.items():
        
        with open(temp + str(index), 'wb') as frag:
            frag.write(chunk)
        
        print('Writing', index)
        track += f'file {index}\n'
    
    with open(temp + 'chunks', 'w') as trackfile:
        trackfile.write(track)
    
    print('Wrote to temp, concatenating')
    
    # TODO - use ffmpeg to concatenate
    
    ffmpeg.input(temp + 'chunks', format = 'concat', safe = 0
    ).output(path, c = 'copy'
    ).run(overwrite_output = True)
    
    # Delete the temp files
    for file in os.listdir(temp):
        os.remove(temp + file)
    
    return

def bk_safe(raw: str,
            path: str,
            timeout: float = 0,
            **kwargs) -> None:
    '''
    Download one segment at a time.
    '''
    
    fragments = re.findall(consts.re.fragments, raw)
    session = requests.Session()
    
    with open(path, 'wb') as output:
        for i, url in enumerate(fragments):
            
            print(f'\r * {i}', end = '')
            
            output.write(
                session.get(url, headers = consts.headers).content
            )
    
    print()

# EOF