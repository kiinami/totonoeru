"""
info.py

Package totonoeru

Created by kinami on 2022-06-28
"""
import questionary
from tmdbv3api import TV, Season, TMDb


def info(res: dict, language: str = None) -> dict:
    """
    Gets the info from The Movie Database.
    """
    # Queries the title
    tmdb = TMDb()
    tmdb.language = language
    info = TV().search(res['title'])

    # Gets the show ID
    if len(info) > 1:
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

    res['title'] = info.name
    res['year'] = info.first_air_date.split('-')[0]
    res['language'] = language
    res['episodes'] = [
        res['episodes'][e.episode_number - 1] | {'title': e.name}
        for i, e in enumerate(Season().details(info.id, res['season']).episodes)
        if i < len(res['episodes'])
    ]

    # Return the info
    return res
