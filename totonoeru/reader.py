"""
reader.py

Package totonoeru

Created by kinami on 2022-06-28
"""
import os

from anitopy import anitopy


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

    # Checks the season is the same for all the files
    assert all([
        r['anime_season'] == filenames[0]['anime_season']
        for r
        in filenames
    ]), 'The season is not the same for all the files'

    # Checks all files have the same extension
    assert all(
        [
            r['file_extension'] == filenames[0]['file_extension']
            for r
            in filenames
        ]
    ), 'The extension is not the same for all the files'


def reader(directory: str = None) -> dict:
    """
    Gets the directory and reads it.
    """
    # Parses the filenames
    res = parse_filenames(directory)

    # Checks the filenames
    check(res)

    # Return the info
    return {
        'directory': directory,
        'title': res[0]['anime_title'],
        'extension': res[0]['file_extension'],
        'season': int(res[0]['anime_season']),
        'episodes': sorted([
            {
                'path': r['file_name'],
                'episode': int(r['episode_number'])
            }
            for r in res
        ], key=lambda x: x['episode'])
    }
