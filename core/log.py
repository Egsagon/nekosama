
class Logger:
    def __init__(self, name: str) -> None:
        self.childs = []
        self.name = name
        self.loglevel = 3 # 1: errs / 2: errs & warn / 3: all
        
    def new_logger(self, name: str) -> 'Logger':
        logger = Logger(name)
        self.childs += [logger]
        return logger
    
    def log(self, *args, sep: str = ' ', color: int = 0, **kwargs) -> None:
        if self.loglevel != 3: return
        print(f'\033[96m[ {self.name.upper(): ^8} ]\033[{color}m', *args, '\033[0m', sep = sep, **kwargs)
    
    def warn(self, *args, sep: str = ' ', **kwargs) -> None:
        if self.loglevel == 1: return
        self.log(*args, sep = sep, color = '93', **kwargs)
    
    def err(self, *args, sep: str = ' ', **kwargs) -> None:
        self.log(*args, sep = sep, color = '91', **kwargs)

class Root(Logger):
    def __init__(self, name: str = 'root') -> None:
        super().__init__(name)


root = Root()
root.log('Started process')