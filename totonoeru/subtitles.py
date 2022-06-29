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

    # Checks all subtitles are in SRT format
    assert all(s['file_extension'] == 'srt' for s in subs), 'Some subtitles are not in SRT format'

    # Adds the subtitles and details
    res['subtitle_dir'] = subs_dir
    subs.sort(key=lambda x: int(x['episode_number']))
    for s in subs:
        res['episodes'][int(s['episode_number']) - 1]['subtitles'] = s['file_name']

    if any([not e.get('subtitles') for e in res['episodes']]):
        print(f'Episodes {", ".join([str(e["episode"]) for e in res["episodes"] if not e.get("subtitles")])} '
              f'have no subtitles')
        if not questionary.confirm(
                f'Episodes {", ".join([str(e["episode"]) for e in res["episodes"] if not e.get("subtitles")])} '
                f'have no subtitles.\nDo you still want to add them?'
        ).ask():
            # Removes the subtitles from the episodes
            for e in res['episodes']:
                e.pop('subtitles', None)
            res.pop('subtitle_dir', None)

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
