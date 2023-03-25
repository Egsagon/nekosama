'''
Logging class.
'''


class Logger:
    def __init__(self, name: str) -> None:
        self.childs = []
        self.name = name
        self.loglevel = 3 # 1: errs / 2: errs & warn / 3: all   
        
        self.set_level(self.loglevel)
    
    def set_level(self, level: int) -> None:
        self.loglevel = level
        
        for c in self.childs:
            c.set_level(level)
        
    def new_logger(self, name: str) -> 'Logger':        
        logger = Logger(name)
        self.childs += [logger]
        return logger
    
    def info(self, *args, sep: str = ' ', color: int = 0, addname = True, **kwargs) -> None:
        
        name = f'\033[96m[ {self.name.upper(): ^8} ]\033[{color}m' if addname else ''
        raw = sep.join(args)
        
        if raw.startswith('\r'):
            raw = raw.replace('\r', '\r' + name + sep)
            print(raw, '\033[0m', sep = sep, **kwargs)
        
        else:
            print(name, raw, '\033[0m', sep = sep, **kwargs)
    
    def log(self, *args, sep: str = ' ', color: int = 0, addname = True, **kwargs) -> None:
        
        if self.loglevel < 3: return
        self.info(*args, sep = sep, color = color, addname = addname, **kwargs)
    
    def warn(self, *args, sep: str = ' ', addname = True, **kwargs) -> None:
        
        if self.loglevel < 2: return
        self.info(*args, sep = sep, color = '93', addname = addname, **kwargs)
    
    def err(self, *args, sep: str = ' ', addname = True, **kwargs) -> None:
        
        self.info(*args, sep = sep, color = '91', addname = addname, **kwargs)
    
    def newline(self) -> None:
        
        print()

class Root(Logger):
    def __init__(self, name: str = 'root') -> None:
        super().__init__(name)


# Create the root logger
root = Root()
# root.log('Started process')

# EOF