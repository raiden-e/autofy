import os
from os.path import dirname

import spotipy

try:
    import config
except ImportError:
    raise ImportError("Please make sure you rename config_template.py to config.py")


def get_spotify_client():
    try:
        cache_path = os.path.join(
            dirname(dirname(__file__)),
            'util',
            'spotify.cache'
        )
        if not os.path.exists(cache_path):
            if config.SPOTIFY['CACHE']:
                with open(cache_path, 'w') as f:
                    f.write(config.SPOTIFY['CACHE'])
            else:
                raise Exception(
                    "Please make sure that you get a spotipy cache string and place it into config.py")

        # print(f"{cache_path} EXISTS: {os.path.exists(cache_path)}")
        _spotify = spotipy.Spotify(
            auth_manager=spotipy.oauth2.SpotifyOAuth(
                username=config.SPOTIFY['NAME'],
                client_id=config.SPOTIFY['ID'],
                client_secret=config.SPOTIFY['HASH'],
                scope=config.SPOTIFY['SCOPE'],
                redirect_uri=config.SPOTIFY['REDIRECT'],
                cache_path=cache_path,
                requests_timeout=10
            )
        )
        return _spotify
    except Exception as e:
        raise Exception(f"ERROR Can't get token", e)
