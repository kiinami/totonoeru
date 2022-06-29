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
    # Gets all the directories
    dirs = [
        d
        for d
        in os.listdir(source_dir)
        if os.path.isdir(os.path.join(source_dir, d))
        and all([f.endswith('.mkv') for f in os.listdir(os.path.join(source_dir, d))])
    ]

    # If there are more than one directory, ask the user to select one
    if len(dirs) > 1:
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
                for i, d in enumerate(dirs)
            ],
            use_shortcuts=True
        ).ask()
    # If there is only one directory, use it
    else:
        directory = os.path.join(source_dir, dirs[0][1])
        print(f'Using {directory}')

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
        'season': int(res[0]['anime_season']),
        'episodes': sorted([
            {
                'path': r['file_name'],
                'episode': int(r['episode_number'])
            }
            for r in res
        ], key=lambda x: x['episode'])
    }
