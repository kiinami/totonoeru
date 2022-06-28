"""
info.py

Package totonoeru

Created by kinami on 2022-06-28
"""
import questionary
from tmdbv3api import TV, Season, TMDb


def info(res: dict) -> dict:
    """
    Gets the info from The Movie Database.
    """
    # Asks the user which language they want to get the metadata in
    language = questionary.select(
        'Please select the language',
        [
            questionary.Choice(
                'English',
                'en',
                shortcut_key='1'
            ),
            questionary.Choice(
                'Japanese',
                'ja',
                shortcut_key='2'
            )
        ],
        use_shortcuts=True
    ).ask()

    # Queries the title
    tmdb = TMDb()
    tmdb.language = language
    info = TV().search(res['title'])

    # Gets the show ID
    if len(res) > 1:
        info = questionary.select(
            'Please select the correct title',
            [
                questionary.Choice(
                    f'{r.name} ({r.first_air_date}) [{r.id}]',
                    value=r,
                    shortcut_key=str(i)
                )
                for i, r in enumerate(info)
            ],
            use_shortcuts=True
        ).ask()
    else:
        info = info[0]

    res['name'] = info.name
    res['year'] = info.first_air_date.split('-')[0]
    res['episodes'] = [
            res['episodes'][e.episode_number - 1] | {'title': e.name}
            for e in Season().details(info.id, 1).episodes
        ]

    # Return the info
    return res
