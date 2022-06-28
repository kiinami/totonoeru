"""
totonoeru.py

Package 

Author:
    kinami

Created:
    25/4/22
"""
import os
import shutil
import subprocess

import anitopy
import click
import questionary
from dotenv import load_dotenv
from tmdbv3api import TV, Season
from alive_progress import alive_it


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


def info(directory: str):
    """
    Gets the info from The Movie Database.
    """
    # Get the filenames
    filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Parse the filenames
    res = [anitopy.parse(f) for f in filenames]

    # Checks the tile is the same for all the files
    assert all([r['anime_title'] == res[0]['anime_title'] for r in res]), 'The title is not the same for all the files'

    # Checks all files have the same extension
    assert all(
        [
            r['file_extension'] == res[0]['file_extension'] 
            for r 
            in res
        ]
    ), 'The extension is not the same for all the files'
    ext = res[0]['file_extension']

    episodes = sorted([
        {
            'filename': e['file_name'],
            'episode': int(e['episode_number'])
        }
        for e in res
    ], key=lambda x: x['episode'])

    # Queries the title
    res = TV().search(res[0]['anime_title'])

    # Gets the show ID
    if len(res) > 1:
        res = questionary.select(
            'Please select the correct title',
            [
                questionary.Choice(
                    f'{r.name} ({r.first_air_date}) [{r.id}]',
                    value=r,
                    shortcut_key=str(i)
                )
                for i, r in enumerate(res)
            ],
            use_shortcuts=True
        ).ask()
    else:
        res = res[0]

    return {
        'name': res.name,
        'year': res.first_air_date.split('-')[0],
        'directory': directory,
        'season': 1,
        'ext': ext,
        'episodes': [
            {
                'episode': e.episode_number,
                'title': e.name,
                'filename': episodes[e.episode_number - 1]['filename']
            }
            for e in Season().details(res.id, 1).episodes
        ]
    }


def add_subs(series: dict, subs_dir: str):
    """
    Adds the subtitles
    """
    # Reads the subtitle files
    subs = [anitopy.parse(f) for f in os.listdir(subs_dir)]

    # Checks there are the same amount of files and subtitles
    assert len(series['episodes']) == len(subs), 'The amount of files and subtitles are not the same'

    # Adds the subtitles and details
    series['subtitle_dir'] = subs_dir
    series['mux_subs'] = all(
        [
            anitopy.parse(e['filename'])['file_extension'] == 'mkv'
            for e
            in series['episodes']
        ]
    ) and questionary.confirm('Do you want to mux the subtitles into the files?').ask()
    subs.sort(key=lambda x: x['episode_number'])
    for e in series['episodes']:
        e['subtitle'] = subs[e['episode'] - 1]['file_name']

    return series


def mux_subs(video_file: str, subtitle_file: str):
    """
    Muxes the subtitles into the video file
    """
    # Deletes the subtitles from the video file
    subprocess.run(
        [
            'mkvmerge',
            '-o',
            video_file.replace('.mkv', '_temp.mkv'),
            '-S',
            video_file
        ],
        check=True,
        stdout=open(os.devnull, 'wb')
    )

    # Adds the subtitles to the video file
    subprocess.run(
        [
            'mkvmerge',
            '-o',
            video_file,
            video_file.replace('.mkv', '_temp.mkv'),
            '--language',
            '0:jpn',
            '--track-name',
            '0:Japanese',
            subtitle_file,
        ],
        check=True,
        stdout=open(os.devnull, 'wb')
    )

    # Deletes the temporary file
    os.remove(video_file.replace('.mkv', '_temp.mkv'))


def move(series: dict):
    """
    Moves the files
    """
    # Lets the user choose the library
    dest_dir = questionary.select(
        'Please select the destination library',
        [
            questionary.Choice(
                f,
                value=os.path.join(os.getenv('TOTONOERU_LIBRARY_DIR'), f)
            )
            for f in os.listdir(os.getenv('TOTONOERU_LIBRARY_DIR'))
            if not f.startswith('.')
        ]
    ).ask()

    # Adds the new folder name to the destination directory
    dest_dir = os.path.join(dest_dir, f'{series["name"]} ({series["year"]})')

    # Creates the destination directory
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Moves the files
    for e in alive_it(series['episodes']):
        dest = shutil.copy2(
            os.path.join(series['directory'], e['filename']),
            os.path.join(
                dest_dir,
                f'{series["name"]} ({series["year"]}) - S{series["season"]:02}E{e["episode"]:02} - {e["title"]}.{series["ext"]}'
            )
        )
        if series['mux_subs']:
            mux_subs(dest, os.path.join(series['subtitle_dir'], e['subtitle']))
            continue
        elif series['subtitle_dir']:
            shutil.copy2(
                os.path.join(series['subtitle_dir'], e['subtitle']),
                os.path.join(
                    dest_dir,
                    f'{series["name"]} ({series["year"]}) - S{series["season"]:02}E{e["episode"]:02} - {e["title"]}.ja.srt'
                )
            )
        os.remove(os.path.join(series['directory'], e['filename']))
        os.symlink(dest, os.path.join(series['directory'], e['filename']))


@click.command()
@click.option('-s', '--subs', type=click.Path(exists=True, file_okay=False), help='Subtitle directory')
def totonoeru(subs):
    """
    Small script to put my media files in my media server.
    """
    # Lets the user select the directory
    directory = select_directory(os.getenv('TOTONOERU_SOURCE_DIR', '~/Downloads'))

    # Creates the series dictionary
    series = info(directory)

    if subs:
        # Validates the subtitles and adds them to the series
        series = add_subs(series, subs)

    # Moves everything
    move(series)

    print('Done!')


if __name__ == '__main__':
    load_dotenv()
    totonoeru()
