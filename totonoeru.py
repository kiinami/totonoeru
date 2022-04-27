"""
totonoeru.py

Package 

Author:
    kinami

Created:
    25/4/22
"""
import os

import anitopy
import click
import questionary
from dotenv import load_dotenv
import tmdbv3api as tmdb
from tmdbv3api import TV, Season


def select_directory(source_dir: str):
    """
    Lets the user select the directory.
    """
    # Get the directory
    directory = questionary.select(
        'Please select the directory',
        [
            questionary.Choice(
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
    Parse the filenames in the directory.
    """
    # Get the filenames
    filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Parse the filenames
    details = [anitopy.parse(f) for f in filenames]

    # Checks the tile is the same for all the files and saves it
    if all([d['anime_title'] == details[0]['anime_title'] for d in details]):
        title = details[0]['anime_title']
    # If not, ask the user to select the title
    else:
        title = questionary.select(
            'Please select the title',
            [
                questionary.Choice(
                    d['anime_title'],
                    shortcut_key=str(i)
                )
                for i, d in enumerate(details)
            ],
            use_shortcuts=True
        ).ask()

    # Creates the details dictionary
    details = {
        'title': title,
        'episodes': [
            {
                'filename': e['file_name'],
                'episode': int(e['episode_number'])
            }
            for e in details
        ]
    }

    # Returns the title and the details
    return details


def get_info(details):
    """
    Gets the info from The Movie Database.
    """
    # Queries the title
    res = TV().search(details['title'])

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

    print([(e.episode_number, e.name) for e in Season().details(res.id, 1).episodes])



@click.command()
@click.option('-s', '--subs', type=click.Path(exists=True, file_okay=False), help='Subtitle directory')
def totonoeru(subs):
    """
    Small script to put my media files in my media server.
    """
    # Lets the user select the directory
    directory = select_directory(os.getenv('TOTONOERU_SOURCE_DIR', '~/Downloads'))

    # Get details from the filenames using anitopy
    details = parse_filenames(directory)

    # Gets the details of the series from The Movie Database
    series = get_info(details)

    # if subs:
    #     # Validates the subtitles and adds them to the series
    #     series = validate_subs(series, subs)
    #
    #     # Moves everything
    #     move(series)
    # else:
    #     # Moves everything
    #     move(series)



if __name__ == '__main__':
    load_dotenv()

    totonoeru()
    print('Done!')
