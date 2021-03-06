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
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help='The directory where the media files are'
)
@click.option(
    '-d',
    '--destination-dir',
    'destination_dir',
    type=click.Path(exists=True, file_okay=False),
    help='The destination directory'
)
@click.option(
    '-t',
    '--sub-dir',
    'sub_dir',
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help='The directory where the subtitles are'
)
@click.option(
    '-l',
    '--language',
    'language',
    type=click.Choice(['en', 'ja']),
    default='ja',
    help='The language of the subtitles'
)
@click.option(
    '-r',
    '--retime-subs',
    'retime',
    is_flag=True,
    help='Retime the subtitles automagically'
)
@click.option(
    '-m',
    '--mux-subs',
    'mux',
    is_flag=True,
    help='Mux the subtitles into the files'
)
def totonoeru(
        source_dir: str,
        destination_dir: str,
        sub_dir: str,
        language: str,
        retime: bool,
        mux: bool
):
    """
    Small script to put my media files in my media server.
    """
    res = reader(source_dir)
    res = info(res, language)
    if sub_dir:
        res = add_subs(res, sub_dir)
    move(res, destination_dir, mux, retime)


if __name__ == '__main__':
    load_dotenv()
    totonoeru()
