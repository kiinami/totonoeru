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
def totonoeru(source_dir: str, library_dir: str, sub_dir: str = None):
    """
    Small script to put my media files in my media server.
    """
    res = reader(source_dir)
    res = info(res)
    res = add_subs(res, sub_dir)
    move(res, library_dir)


if __name__ == '__main__':
    load_dotenv()
    totonoeru()
