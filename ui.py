'''
    Simple tkinter ui example for
    the core module.
'''

import re
import core
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmsg
from tkinter.ttk import Progressbar

# Debug level
core.root.set_level(3) # TODO


class App(tk.Tk):
    def __init__(self) -> None:
        '''
        Represents an instance of the app.
        ----------------------------------
        '''
        
        # Init window
        tk.Tk.__init__(self)
        self.title('NS DOWNLOADER')
        self.geometry('400x650')
        
        self.configure(bg = '#fff')
        
        # Init client
        self.client = core.scrapper.Comm()
        self.anime: core.scrapper.Anime = None
        self.episodes: core.scrapper.Episode = None
        
        # Add widgets
        main = tk.LabelFrame(self, text = 'Download NS',
                             font = ('Roboto', 20),
                             labelanchor = 'n', bg = '#fff')
        
        footer = tk.Frame(main, bg = '#fff')
        
        url_box = tk.Frame(main, bg = '#fff')
        self.url_entry = tk.Entry(url_box, bg = '#fff', fg = '#3366CC')
        url_load = tk.Button(url_box, text = '↺', width = 5, height = 1, command = self.load,
                             bg = '#fff')
        
        self.select = tk.Listbox(main, selectmode = 'multiple', selectbackground = '#60100B',
                                 selectborderwidth = 0, bg = '#fff')
        self.confirm = tk.Button(footer, text = 'Download', command = self.download,
                                 state = 'disabled', height = 2, bg = '#60100B', fg = '#fff')
        
        self.url_entry.bind('<Return>', self.load)
        
        self.info = tk.StringVar()
        info = tk.Label(footer, textvariable = self.info, fg = 'red', bg = '#fff', font = ('Arial', 12))
        self.progress = Progressbar(footer)
        self.curprogress = Progressbar(footer)
        
        self.quality = tk.StringVar(self, '-- Select quality --')
        self.qualities = tk.OptionMenu(footer, self.quality,
                                       'best', 'middle', 'worst', 1080, 720, 480)
        
        # Pack
        self.url_entry.pack(side = 'left', expand = True, fill = 'x')
        url_load.pack(side = 'right')
        url_box.pack(fill = 'x', padx = 24, pady = 24)
        
        self.select.pack(expand = True, fill = 'both', padx = 24, pady = 24)
        
        self.qualities.pack(fill = 'x', padx = 24, pady = (24, 5))
        self.confirm.pack(fill = 'x', padx = 24, pady = (5, 24))
        
        footer.pack(side = 'bottom', fill = 'x')
        main.pack(expand = True, fill = 'both', padx = 24, pady = 24)
        
        info.pack()
        self.curprogress.pack(fill = 'x', padx = 5, pady = (0, 5))
        self.progress.pack(fill = 'x', padx = 5, pady = (0, 5))
    
    def load(self, *_) -> None:
        '''
        Load episodes to the selection list.
        ------------------------------------
        '''
        
        url = self.url_entry.get()
        
        # Error protection
        if not re.search(r'https:\/\/neko-sama\.fr\/anime\/info\/.*_vostfr', url):
            return tkmsg.showerror('Error', 'Invalid url: ' + url)
        
        print('loading', url)
        self.info.set('Fetching anime...')
        self.curprogress.configure(value = .5)
        self.update()
        
        # Load
        self.anime = self.client.get_anime(url)
        
        print('fetched anime', self.anime)
        self.curprogress.step(40)
        self.update()
        
        self.episodes = self.anime.get_episodes()
        
        # Insert to list
        names = [e.name for e in self.episodes]
        self.select.insert(0, *names)
        
        # Enable download button
        self.confirm.configure(state = 'normal')
        
        # self.progress.stop()
        self.curprogress.configure(value = 0)
        self.info.set('Ready')
    
    def download(self, *_) -> None:
        '''
        Start downloading the episodes.
        -------------------------------
        '''
        
        # Get path
        path = tkfd.askdirectory() + '/'
        
        # Get quality
        qual = self.quality.get()
        
        # Error protection
        if '--' in qual: return tkmsg.showerror('Please select a quality.')
        
        if qual.isdecimal(): qual = int(qual)
        
        # Get episodes
        episodes = []        
        names = [self.select.get(i) for i in self.select.curselection()]
        
        if len(names):
            for name in names:
                for ep in self.episodes:
                    if ep.name == name:
                        episodes += [ep]
        
        # If nothing specified, download all
        else: episodes = self.episodes
        
        # Send confirm popup
        msg = f'Download {len(episodes)} episodes at {path} with quality {qual}?'
        if not tkmsg.askyesno('Confirm Download', msg): return
        
        self.info.set('Starting...')
        self.update()
        print('Downloading', episodes, 'on', path, 'with quality', qual)
        
        self.progress.configure(mode = 'determinate')
        self.curprogress.configure(mode = 'determinate')
        
        def on_dl(cur, full, status) -> None:
            # Called each download update
            
            self.info.set(f'{status}: {cur}/{full}')
            self.curprogress.config(value = (cur / full) * 100)
            
            # Overall progress only shows download progress
            # because checking/writing too fast
            if status == 'Downloading':
                self.progress.step((100 / full) / len(episodes))
            
            self.update()
        
        for episode in episodes:
            episode: core.scrapper.Episode
            
            self.info.set('Grabbing provider...')
            self.update()
            
            episode.download(path + episode.raw_name, qual,
                             looping_callback = on_dl)
            
            print('downloaded', episode)
        
        # Finish
        tkmsg.showinfo('Finished', f'Successfuly downloaded {len(episodes)} at {path}.')
        
        self.progress.configure(value = 0)
        self.curprogress.configure(value = 0)
        self.info.set('Done.')

if __name__ == '__main__': App().mainloop()

# EOF