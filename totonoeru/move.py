"""
move.py

Package totonoeru

Created by kinami on 2022-06-28
"""
import os
import shutil

from alive_progress import alive_it

from subtitles import mux_subs, retime_subs


def move(res: dict, destination: str, mux: bool, retime: bool):
    """
    Moves the files
    """
    # Adds the new folder name to the destination directory
    destination = os.path.join(destination, f'{res["title"]} ({res["year"]})')

    # Creates the destination directory
    if not os.path.exists(destination):
        os.makedirs(destination)

    for e in alive_it(res['episodes']):
        # Copies the file
        dest = shutil.copy2(
            os.path.join(res['directory'], e['path']),
            os.path.join(
                destination,
                f'{res["title"]} ({res["year"]}) - S{res["season"]:02}E{e["episode"]:02} - {e["title"]}'
                f'.{res["extension"]}'
            )
        )

        if e.get('subtitles'):
            # Retimes the subtitles
            if retime:
                retime_subs(dest, os.path.join(res['subtitle_dir'], e['subtitles']))

            # If mux is True, muxes the subtitles
            if mux:
                mux_subs(dest, os.path.join(res['subtitle_dir'], e['subtitles']), res['language'])
                # Continues to the next episode
                continue
            else:
                # Else, copies the subtitles
                shutil.copy2(
                    os.path.join(res['subtitle_dir'], e['subtitles']),
                    os.path.join(
                        destination,
                        f'{res["title"]} ({res["year"]}) - S{res["season"]:02}E{e["episode"]:02} - {e["title"]}'
                        f'.{res["language"]}.srt'
                    )
                )

        # Removes the old file
        os.remove(os.path.join(res['directory'], e['path']))
        # Symlinks the new file
        os.symlink(dest, os.path.join(res['directory'], e['path']))
