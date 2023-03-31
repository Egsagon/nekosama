import re
import base64
import ffmpeg
import requests

import os
import time
import threading
import subprocess
from copy import copy

import utils
import consts

class Episode:
    def __init__(self, url: str, session: requests.Session = None) -> None:
        '''
        Represents an Anime episode.
        '''
        
        # TODO - Verify that url is a valid episode url
        
        self.url = url
        self.session = session or requests.Session()
        self.providers = []
        self.cache = {}
    
    def get(self,
            url: str,
            headers: dict = None,
            cache: bool = True) -> requests.Response:
        '''
        Get a page from the cache or fetch it.
        '''
        
        if cache and url in self.cache:
            print('USING CACHED')
            return self.cache.get(url)
        
        req = self.session.get(url, headers = headers)
        
        # Error protection
        if not req.ok: raise ConnectionError(req.status_code, req.content)
        
        self.cache[url] = req
        return req
    
    def get_providers(self) -> list[str]:
        '''
        Get all the available providers for this episode.
        '''
        
        raw = self.get(self.url).text
        
        self.providers = [url.split('= ')[1][1:-2]
                          for url in re.findall(consts.re.providers, raw)]
        
        return self.providers

    def get_fragments(self,
                      provider: str = consts.provider.BEST,
                      quality: str | int = consts.quality.BEST) -> list[str]:
        '''
        Get the list of fragment links for a specific provider (default first)
        and quality (default best).
        '''
        
        # Get provider url (link to the player)
        if not len(self.providers): self.get_providers()
        provider_url = utils.select_provider(self.providers, provider)
        
        # Get the provider link to its script
        src = self.get(provider_url , headers = consts.headers).text
        res = re.findall(consts.re.script, src)[0][:-2]
        
        # Get the m3u file url
        src = self.get(res, headers = consts.headers).text
        res = re.findall(consts.re.m3u8, src)[0]
        raw = base64.b64decode(res).decode()
        m3u = re.findall(consts.re.m3u8_urls, raw)[0].replace('\\', '')[:-1]
        
        # Get the appropriate video quality
        quals = self.get(m3u, headers = consts.headers).text
        quals = [q.split() for q in re.findall(consts.re.qualities, quals)]
        quals = {int(''.join(re.findall(r'\d*', q))): u for q, u in quals}
        qual = utils.select_quality(quals, quality)
        
        # Get the framgents list
        src = self.get(qual, headers = consts.headers).text
        return re.findall(consts.re.fragments, src)
    
    def get_fragment(self, req: requests.PreparedRequest,
                     data: dict = None,
                     todo: list = None,
                     timeout: int = .05) -> bytes | None:
        '''
        Attempt to download a video fragment.
        If data and todo are specified, will dump the fragment
        into them instead of returning.
        '''
        
        raw = self.session.send(req).content
        
        while b'<html>' in raw:
            # Requests has failed
            
            # Dump back into todo
            if todo is not None:
                return todo.append(req)

            # Retry in a bit
            time.sleep(timeout)
            raw = self.session.send(req).content
        
        else:
            if data is None: return raw
            
            # TODO regex not working sometimes
            # key = int(re.findall(consts.re.frag_index, req.url)[0][:-3])
            key = int(req.url.split('/')[-1].split('.')[0])
            
            data[key] = raw
    
    def write_fragment(self, data: bytes, pipe: str, chunk_size = 8192) -> None:
        '''
        Write a fragment bytes to a pipe.
        
        From https://stackoverflow.com/questions/74256808
        '''
        
        pipe_input = os.open(pipe, os.O_WRONLY)
        
        for i in range(0, len(data), chunk_size):
            os.write(pipe_input, data[i:chunk_size + i])
        
        os.close(pipe_input)
    
    def download(self,
                 path: str,
                 provider: str = consts.provider.BEST,
                 quality: str = consts.quality.BEST,
                 timeout: float = .051) -> None:
        '''
        Download the episode to a specific path.
        '''
        
        fragments = self.get_fragments(provider, quality)
        print(len(fragments))
        
        # Generate requests
        req = [requests.Request('GET', url, consts.headers).prepare() for url in fragments]
        
        data = {}
        todo = copy(req)
        
        while len(todo):
            cur = todo.pop(0)
            threading.Thread(target = self.get_fragment, args = [cur, data, todo, timeout]).start()
            time.sleep(timeout)
            
            total = len(req)
            done = total - len(data)
            
            print('\rDownloading', done, '/', total, end = '')
        
        print('Checking integrity')
        
        for i, req_ in enumerate(req):
            
            if not i in data.keys():
                print('missing', i)
                raw = self.get_fragment(req_, timeout = timeout)
                data[i] = raw
                
        print('Writing')
        
        tmp = './tmp/'
        if not os.path.exists(tmp): os.mkdir(tmp)
        
        with open(tmp + 'fragments.txt', 'a') as fragments_list:
            
            for index, raw in data.items():
            
                frag_path = tmp + str(index)
            
                with open(frag_path, 'wb') as output:
                    output.write(raw)
            
                fragments_list.write(f'file {frag_path}\n')
        
        print('Concatenating')
        
        # ffmpeg.input(tmp + 'fragments.txt', format = 'concat', safe = 0).output(path, c = 'copy').run()
        
        # Delete temp dir
        os.remove(tmp)

anime = Episode('https://neko-sama.fr/anime/episode/9520-tensei-shitara-slime-datta-ken-01_vostfr')
start = time.time()
anime.download('./test1.mp4', quality = consts.quality.WORST)
print('Done in', time.time() - start)

# EOF