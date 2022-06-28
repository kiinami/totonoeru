"""
subtitles.py

Package totonoeru

Created by kinami on 2022-06-28
"""
import os
import subprocess

import questionary
from anitopy import anitopy
from iso639 import languages


def add_subs(res: dict, subs_dir: str):
    """
    Adds the subtitles
    """
    # Reads the subtitle files
    subs = [anitopy.parse(f) for f in os.listdir(subs_dir)]

    # Checks there are the same amount of files and subtitles
    assert len(res['episodes']) == len(subs), 'The amount of files and subtitles are not the same'

    # Adds the subtitles and details
    res['subtitle_dir'] = subs_dir
    res['mux_subs'] = all(
        [
            anitopy.parse(e['path'])['file_extension'] == 'mkv'
            for e
            in res['episodes']
        ]
    ) and questionary.confirm('Do you want to mux the subtitles into the files?').ask()
    subs.sort(key=lambda x: x['episode_number'])
    for e in res['episodes']:
        e['subtitles'] = subs[e['episode'] - 1]['file_name']

    return res


def mux_subs(video_file: str, subtitle_file: str, language: str):
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

    # Gets the language standard
    language = languages.get(alpha2=language)

    # Adds the subtitles to the video file
    subprocess.run(
        [
            'mkvmerge',
            '-o',
            video_file,
            video_file.replace('.mkv', '_temp.mkv'),
            '--language',
            f'0:{language.part2b}',
            '--track-name',
            f'0:{language.name}',
            subtitle_file,
        ],
        check=True,
        stdout=open(os.devnull, 'wb')
    )

    # Deletes the temporary file
    os.remove(video_file.replace('.mkv', '_temp.mkv'))
