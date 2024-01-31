'''
Nekosama CLI.
'''

import click
import nekosama

@click.group()
def neko():
    pass

@neko.command()
@click.argument('url')
@click.option('--output', '-o', help = 'Output file or directory', default = './')
@click.option('--quality', '-q', help = 'Video quality', default = 'best')
def download(url: str, output: str, quality: str) -> None:
    '''
    Download an anime.
    '''
    
    cls = nekosama.Episode if '/episode/' in url else nekosama.Anime
    
    cls(url).download(output, quality = quality)

if __name__ == '__main__':
    neko()

# EOF
