'''
Simple tkinter ui example
for the nekosama API.

TODO - Threads?
'''

import nekosama

import tkinter as tk
import tkinter.filedialog as tkf
import tkinter.messagebox as tkm
from tkinter.ttk import Progressbar

from time import time

def sleep(root: tk.Tk, duration: float) -> None:
    
    start = time()
    while time() + duration < start:
        root.update()

class App(tk.Tk):
    def __init__(self) -> None:
        '''
        Represents an instance of the app.
        '''
        
        # Init window
        tk.Tk.__init__(self)
        self.title('Neko Sama Downloader')
        self.geometry('400x500')
        pad = {'padx': 12, 'pady': 12}
        
        self.client = nekosama.Client()
        self.anime: nekosama.Anime = None
        
        # Add widgets
        main = tk.LabelFrame(self,
                             text = '  Search  ',
                             font = ('Roboto', 20),
                             labelanchor = 'n')

        # Query entry section
        url_box = tk.Frame(main)
        self.url = tk.Entry(url_box)
        self.url.bind('<Return>', self.search)
        url_get = tk.Button(url_box, text = 'GET', command = self.search)
        
        # Query response and progress section
        self.selection = tk.Listbox(main, selectmode = 'multiple')
        self.start = tk.Button(main, text = 'Download', height = 2,
                               command = self.download)
        
        self.local_progress = Progressbar(main)
        self.global_progress = Progressbar(main)

        # Pack widgets
        self.url.pack(side = 'left', fill = 'x', expand = True)
        url_get.pack(side = 'right', padx= (12, 0))
        url_box.pack(fill = 'x', **pad)
        
        self.selection.pack(fill = 'both', expand = True, padx = 12)
        self.start.pack(fill = 'x', **pad)
        self.local_progress.pack(fill = 'x', padx = 12)
        self.global_progress.pack(fill = 'x', padx = 12, pady = (6, 12))
        
        main.pack(expand = True, fill = 'both', **pad)
    
    def select_anime(self, animes: list[nekosama.Episode]) -> nekosama.Anime:
        '''
        Choose an anime.
        '''
        
        def valid(*_) -> None:
            idx = sel.curselection()
            
            if not(len(idx)):
                return tkm.showerror('Error', 'Select an anime.')
            
            self.anime = animes[idx[0]]
            pop.destroy()
            pop.quit()
        
        pop = tk.Toplevel(self)
        pop.geometry('600x300')
        pop.title('Choose an anime')
        
        sel = tk.Listbox(pop)
        sel.insert(0, *[a.title for a in animes])
        sel.pack(fill = 'both', expand = True, padx = 12, pady = 12)
        tk.Button(pop, text = 'OK', command = valid).pack(fill = 'both')
        
        pop.mainloop()
        return self.anime

    def search(self, *_) -> None:
        '''
        Search an anime.
        '''
        
        value = self.url.get()

        if 'https://' in value:
            try:
                animes = [self.client.get_anime(value)]
            
            except ConnectionError as e:
                return tkm.showerror('Error', 'Invalid url', value, e)
        
        else:
            animes = self.client.search(value, limit = 10)
        
        # Choose one anime
        anime = self.select_anime(animes)
        
        episodes = anime.get_episodes()
        
        # Add to selection
        self.selection.delete(0, tk.END)
        self.selection.insert(0, *[e.name for e in episodes])
    
    def update_bar(self, status: str, cur: int, total: int | None) -> None:
        '''
        Called by the download method to update the bar positions.
        '''
        
        print(status, cur, total, cur / total * 100)
        
        self.title(status)
        
        if total is not None:
            self.local_progress.config(value = cur / total * 100)
        
        else:
            self.local_progress.config(mode = 'indeterminate')
            self.local_progress.step()
        
        self.update()
    
    def download(self, *_) -> None:
        '''
        Download one or multiple episodes.
        '''
        
        episodes = [self.anime.episodes[i] for i in
                    self.selection.curselection()]
        
        # If none selected, select all
        if not len(episodes): episodes = self.anime.episodes
        
        # Confirmation popup
        if not tkm.askyesno('Confirm', f'Download {len(episodes)} episodes?'):
            return
        
        # Get directory path
        path = tkf.askdirectory(title = 'Select output', mustexist = True)
        if not path: tkm.showerror('Error', 'Please specify a directory.')
        
        print('Downloading', episodes, 'in', path)
        
        self.local_progress.config(mode = 'determinate', value = 0)
        
        self.global_progress.config(mode = 'determinate', value = 0,
                                    length = len(episodes))
        
        # Download
        for episode in episodes:
            
            # TODO threadify
            # episode.download(path + episode.name + '.mp4')
            
            episode.download(
                path + episode.name + '.mp4',
                method = 'ffmpeg', # thread_
                callback = self.update_bar,
                quiet = True
            )
            
            sleep(self, 3)
            self.global_progress.step()
            self.update()
        
        tkm.showinfo('Done', 'Operation finished.')

if __name__ == '__main__':
    App().mainloop()

# EOF