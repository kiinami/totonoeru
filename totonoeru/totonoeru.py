"""
totonoeru.py

Package 

Author:
    kinami

Created:
    25/4/22
"""

import click
from dotenv import load_dotenv

from info import info
from move import move
from reader import reader
from subtitles import add_subs


@click.command()
@click.option(
    '-s',
    '--source-dir',
    'source_dir',
    envvar='SOURCE_DIR',
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help='The parent directory to read the files from'
)
@click.option(
    '-l',
    '--library-dir',
    'library_dir',
    envvar='LIBRARY_DIR',
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help='The library to move the files to'
)
@click.option(
    '-d',
    '--media-dir',
    'media_dir',
    type=click.Path(exists=True, file_okay=False),
    help='The directory where the media files are'
)
@click.option(
    '-t',
    '--sub-dir',
    'sub_dir',
    type=click.Path(exists=True, file_okay=False),
    help='The directory where the subtitles are'
)
@click.option(
    '-l',
    '--language',
    'language',
    type=click.Choice(['en', 'ja']),
    help='The language of the subtitles'
)
@click.option(
    '-m/-c',
    '--mux-subs/--copy-subs',
    'mux',
    help='Mux the subtitles into the files',
    default=None
)
def totonoeru(
        source_dir: str,
        library_dir: str,
        media_dir: str = None,
        sub_dir: str = None,
        language: str = None,
        mux: bool = None,

):
    """
    Small script to put my media files in my media server.
    """
    res = reader(source_dir, media_dir)
    res = info(res, language)
    res, mux = add_subs(res, sub_dir, mux)
    move(res, library_dir, mux)


if __name__ == '__main__':
    load_dotenv()
    totonoeru()
