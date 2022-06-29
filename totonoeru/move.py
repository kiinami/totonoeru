"""
move.py

Package totonoeru

Created by kinami on 2022-06-28
"""
import os
import shutil

import questionary
from alive_progress import alive_it

from subtitles import mux_subs


def move(res: dict, library_dir: str, mux: bool):
    """
    Moves the files
    """
    # Lets the user choose the library
    destination = questionary.select(
        'Please select the destination library',
        [
            questionary.Choice(
                f,
                value=os.path.join(library_dir, f)
            )
            for f in os.listdir(library_dir)
            if not f.startswith('.')
        ]
    ).ask()

    # Adds the new folder name to the destination directory
    destination = os.path.join(destination, f'{res["title"]} ({res["year"]})')

    # Creates the destination directory
    if not os.path.exists(destination):
        os.makedirs(destination)

    # Moves the files
    for e in alive_it(res['episodes']):
        dest = shutil.copy2(
            os.path.join(res['directory'], e['path']),
            os.path.join(
                destination,
                f'{res["title"]} ({res["year"]}) - S{res["season"]:02}E{e["episode"]:02} - {e["title"]}'
                f'.{res["extension"]}'
            )
        )

        if e.get('subtitles'):
            if mux:
                mux_subs(dest, os.path.join(res['subtitle_dir'], e['subtitles']), res['language'])
                continue
            else:
                shutil.copy2(
                    os.path.join(res['subtitle_dir'], e['subtitles']),
                    os.path.join(
                        destination,
                        f'{res["title"]} ({res["year"]}) - S{res["season"]:02}E{e["episode"]:02} - {e["title"]}'
                        f'.{res["language"]}.srt'
                    )
                )
        os.remove(os.path.join(res['directory'], e['path']))
        os.symlink(dest, os.path.join(res['directory'], e['path']))
