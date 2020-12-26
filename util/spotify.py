import os
from os.path import dirname

import config
import spotipy


def get_spotify_client():
    try:
        cache_path = os.path.join(
            dirname(dirname(__file__)),
            'util',
            'spotify.cache'
        )
        if not os.path.exists(cache_path):
            if config.SPOTIPYCACHE:
                with open(cache_path, 'w') as f:
                    f.write(config.SPOTIPYCACHE)
            else:
                raise "Please make sure that you get a spotipy cache string and place it into config.py"

        print(f"{cache_path} EXISTS: {os.path.exists(cache_path)}")
        _spotify = spotipy.Spotify(
            auth_manager=spotipy.oauth2.SpotifyOAuth(
                username=config.SPOTIPYUN,
                client_id=config.SPOTIPYID,
                client_secret=config.SPOTIPYHS,
                scope=config.SPOTIPYSC,
                redirect_uri=config.SPOTIPYRU,
                cache_path=cache_path
            )
        )
        return _spotify
    except Exception as e:
        raise(f"ERROR Can't get token for {config.SPOTIPYUN}", e)
