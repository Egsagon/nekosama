'''
List of backends used by the 
core module to download animes.

TODO - quiet arg on all backends
TODO - refactor all backends
'''

import os
import re
import time
import copy

import shutil
import requests
import threading

from typing import Callable

from nekosama import consts
from nekosama import utils

# Get the FFMPEG path
FFMPEG = shutil.which('ffmpeg')


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
    
    if FFMPEG is None and 'ffmpeg' in method:
        print('[ BK ] FFMPEG is not installed, falling back to safe')
    
    return eval('bk_' + method)


def bk_ffmpeg(raw: str,
              path: str,
              callback: Callable = None,
              quiet: bool = False,
              **kwargs) -> None:
    '''
    Download using the ffmpeg download feature.
    '''

    # Write the m3u8 file for ffmpeg
    with open('temp.m3u', 'w') as file: file.write(raw)
    
    command = [
        FFMPEG,
        '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',
        '-i', 'temp.m3u',
        '-acodec', 'copy',
        '-vcodec', 'copy',
        path, '-y'
    ]
    
    def log(line: str) -> None:
        '''Called each time ffmpeg outputs a line.'''
        
        if 'https://' in line and '.ts' in line:
            cur = line.split('.ts')[0].split('/')[-1]
            
            if callback is not None:
                callback(cur)
        
        if not quiet:
            print(line, end = '')
    
    code = utils.popen(command, log)
    
    if code != 0: print('Command raised error', code)
    
    # Delete the temp file
    os.remove('temp.m3u')

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
                   callback: Callable = None,
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
        if callback is not None: callback(len(data))
        # print('*', len(data), len(todo))
    
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
              callback: Callable = None,
              **kwargs) -> None:
    '''
    Download each fragment using threads.
    Theorically faster.
    '''
    
    # Fetch the chunks
    chunks = bk_base_thread(raw = raw,
                            timeout = timeout,
                            callback = callback)
    
    # Write them to the file
    with open(path, 'wb') as output:
        for key in sorted(chunks.keys()):
            print('Writing', key)
            if callback is not None: callback(key)
            output.write(chunks[key])
    
    return
    
def bk_thread_ffmpeg(raw: str,
                     path: str,
                     timeout: float = .05,
                     callback: Callable = None,
                     **kwargs) -> None:
    '''
    Same as thread, but uses ffmpeg to concatenate.
    '''
    
    # Fetch the chunks
    chunks = bk_base_thread(raw = raw,
                            timeout = timeout,
                            callback = callback)
    
    temp = 'temp/'
    track = []
    
    # Create temp folder if needed
    if not os.path.exists(temp): os.mkdir(temp)
    
    for index, chunk in chunks.items():
        
        frag_path = temp + str(index) + '.ts'
        
        with open(frag_path, 'wb') as frag:
            frag.write(chunk)
        
        print('Writing', index)
        track += [f'file {index}.ts']
    
    with open(temp + 'track', 'w') as file:
        file.write('\n'.join(track))
    
    print('Wrote to temp, concatenating')
    
    # Concatenate ts files and run ffmpeg
    # https://superuser.com/questions/692990
    
    command = [
        FFMPEG, '-f', 'concat',
        '-safe', '0',
        '-i', temp + 'track',
        '-c', 'copy', path, '-y'
    ]
    
    assert utils.popen(command, lambda l: print([l])) == 0
    
    print('Done. Erasing cache')
    
    # Delete the temp files
    for file in os.listdir(temp):
        os.remove(temp + file)

def bk_safe(raw: str,
            path: str,
            timeout: float = 0,
            callback: Callable = None,
            **kwargs) -> None:
    '''
    Download one segment at a time, and concatenate their
    bytes before writing to a file.
    '''
    
    fragments = re.findall(consts.re.fragments, raw)
    session = requests.Session()
    
    with open(path, 'wb') as output:
        for i, url in enumerate(fragments):
            
            if callback: callback(str(i))
            # print(f'\r * {i}', end = '')
            
            output.write(
                session.get(url, headers = consts.headers).content
            )
            
            time.sleep(timeout)
    
    print()

# EOF