'''
List of backends used by the 
core module to download animes.
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
        method = 'safe'
    
    return eval('bk_' + method)


def bk_ffmpeg(raw: str,
              path: str,
              callback: Callable = None,
              quiet: bool = False,
              **kwargs) -> None:
    '''
    Download using the ffmpeg download feature.
    '''

    # Get the total count
    lenght = len(re.findall(consts.re.fragments, raw))

    # Write the m3u8 file for ffmpeg
    with open('temp.m3u', 'w') as file: file.write(raw)
    
    # Create the FFMPEG command
    command = [
        FFMPEG,
        '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',
        '-i', 'temp.m3u',
        '-acodec', 'copy',
        '-vcodec', 'copy',
        path, '-y'
    ]
    
    def log(line: str) -> None:
        # Decide whether to execute the callback or not
        # for each line.
        
        key = re.findall(consts.re.frag_index, line)
        
        if len(key) and callback is not None:
            callback('downloading', int(key[0]) + 1, lenght)

        if not quiet:
            print(line, end = '')
    
    # Start FFMPEG
    assert utils.popen(command, log) == 0
    
    # Delete the m3u8 file
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
                   quiet: bool = False,
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
        if callback is not None: callback('downloading', len(data), len(chunks))
        
        if not quiet:
            print(f'[ BK ] Downloading chunk ({len(todo)} left)')
    
    # Check for missing chunks
    for i in range(len(chunks)):
        if not i in data.keys():
            
            # Debug
            if not quiet: print('Downloading missing', i)
            
            if callback is not None:
                callback('downloading missing', i, len(chunks))
            
            # Get chunk request
            mreq = [r for r in reqs if r.url.endswith(f'{i}.ts')][0]
            data[i] = dl_frag(mreq, timeout, session)
    
    return data

def bk_thread(raw: str,
              path: str,
              timeout: float = .05,
              callback: Callable = None,
              quiet: bool = False,
              **kwargs) -> None:
    '''
    Download each fragment using threads.
    Theorically faster.
    '''
    
    # Fetch the chunks
    chunks = bk_base_thread(raw = raw,
                            timeout = timeout,
                            callback = callback,
                            quiet = quiet)
    
    # Write them to the file
    with open(path, 'wb') as output:
        for key in sorted(chunks.keys()):
            
            if not quiet:
                print(f'\r[ BK ] Downloading: {key}/{chunks}', end = '')
            
            if callback is not None:
                callback('writing', key, len(chunks))
            
            output.write(chunks[key])
        
        if not quiet: print()
    
    return
    
def bk_thread_ffmpeg(raw: str,
                     path: str,
                     timeout: float = .05,
                     callback: Callable = None,
                     quiet: bool = False,
                     **kwargs) -> None:
    '''
    Same as thread, but uses ffmpeg to concatenate.
    '''
    
    # Fetch the chunks
    chunks = bk_base_thread(raw = raw,
                            timeout = timeout,
                            callback = callback,
                            quiet = quiet)
    
    temp = 'temp/'
    track = []
    
    # Create temp folder if needed
    if not os.path.exists(temp): os.mkdir(temp)
    
    for index, chunk in chunks.items():
        
        frag_path = temp + str(index) + '.ts'
        
        with open(frag_path, 'wb') as frag:
            frag.write(chunk)
        
        if not quiet:
            print(f'\r[ BK ] Writing {index}/{len(chunks)}', end = '')
        
        if callback is not None:
            callback('writing', index, len(chunks))
        
        track += [f'file {index}.ts']
    
    with open(temp + 'track', 'w') as file:
        file.write('\n'.join(track))
    
    if not quiet: print('[ BK ] Concatenating')
    
    # Concatenate ts files with ffmpeg
    
    command = [
        FFMPEG, '-f', 'concat',
        '-safe', '0',
        '-i', temp + 'track',
        '-c', 'copy', path, '-y'
    ]
    
    def log(line: str) -> None:
        # Decide to execute the callback
        # for a line or not.
        
        if line.startswith('\nframe='):
            cur = line[8:].split()[0]
            
            if callback is not None:
                callback('concatenating', int(cur), None)
        
        if not quiet:
            print(line, end = '')
    
    assert utils.popen(command, log) == 0
    
    if not quiet: print('Deleting temp files')
    
    # Delete the temp files
    for file in os.listdir(temp):
        os.remove(temp + file)

def bk_safe(raw: str,
            path: str,
            timeout: float = 0,
            callback: Callable = None,
            quiet: bool = False,
            **kwargs) -> None:
    '''
    Download one segment at a time, and concatenate their
    bytes before writing to a file.
    '''
    
    fragments = re.findall(consts.re.fragments, raw)
    session = requests.Session()
    
    with open(path, 'wb') as output:
        for i, url in enumerate(fragments):
            
            if callback: callback('downloading', i, len(fragments))
            
            if not quiet:
                print('Downloading', i)
            
            output.write(
                session.get(url, headers = consts.headers).content
            )
            
            time.sleep(timeout)
    
    print()

# EOF