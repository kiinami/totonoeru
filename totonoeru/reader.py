"""
reader.py

Package totonoeru

Created by kinami on 2022-06-28
"""
import os

import questionary
from anitopy import anitopy


def select_directory(source_dir: str):
    """
    Lets the user select the directory.
    """
    # Get the directory
    directory = questionary.select(
        'Please select the directory',
        [
            questionary.Choice(
                d,
                os.path.join(source_dir, d),
                disabled='Not valid' if not all(
                    [f.endswith('.mkv') for f in os.listdir(os.path.join(source_dir, d))]) else None,
                shortcut_key=str(i)
            )
            for i, d in enumerate(os.listdir(source_dir))
            if os.path.isdir(os.path.join(source_dir, d))
        ],
        use_shortcuts=True
    ).ask()

    # Return the directory
    return directory


def parse_filenames(directory: str):
    """
    Parses the filenames.
    """
    # Get the filenames
    filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Parse the filenames
    res = [anitopy.parse(f) for f in filenames]

    # Return the info
    return res


def check(filenames: list):
    """
    Checks the filenames.
    """
    # Checks the tile is the same for all the files
    assert all([
        r['anime_title'] == filenames[0]['anime_title']
        for r
        in filenames
    ]), 'The title is not the same for all the files'

    # Return
    return


def reader(source_dir: str = None, directory: str = None) -> dict:
    """
    Gets the directory and reads it.
    """
    # Get the directory
    if directory is None:
        directory = select_directory(source_dir)

    # Parses the filenames
    res = parse_filenames(directory)

    # Checks the filenames
    check(res)

    # Return the info
    return {
        'directory': directory,
        'title': res[0]['anime_title'],
        'extension': res[0]['file_extension'],
        'episodes': [
            {
                'path': os.path.join(directory, r),
                'episode': r['episode']
            }
            for r in res
        ]
    }
