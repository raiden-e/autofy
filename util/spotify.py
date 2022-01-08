import os
from os.path import dirname

if __name__ == '__main__':
    import sys
    pth = os.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config
    sys.path = pth
else:
    import config
import spotipy


def get_cache_path() -> str:
    cache_path = os.path.join(
        dirname(dirname(__file__)),
        'util',
        'spotify.cache'
    )
    # if not os.path.exists(cache_path):
    #     if config.SPOTIFY['CACHE'] is None:
    #         raise Exception(
    #             "Please make sure that you get a spotipy cache string and place it into config.py")
    #     with open(cache_path, 'w', encoding='utf-8') as f:
    #         f.write(config.SPOTIFY['CACHE'])
    return cache_path


def get_spotify_client() -> spotipy.Spotify:
    try:
        # print(f"{cache_path} EXISTS: {os.path.exists(cache_path)}")
        _spotify = spotipy.Spotify(
            auth_manager=spotipy.oauth2.SpotifyOAuth(
                username=config.SPOTIFY['NAME'],
                client_id=config.SPOTIFY['ID'],
                client_secret=config.SPOTIFY['HASH'],
                scope=config.SPOTIFY['SCOPE'],
                redirect_uri=config.SPOTIFY['REDIRECT'],
                cache_path=get_cache_path(),
                requests_timeout=10
            )
        )
        return _spotify
    except Exception as e:
        raise Exception("ERROR Can't get token", e)


def get_new_token():
    # _sp = get_spotify_client()
    oauth = spotipy.oauth2.SpotifyOAuth
    spotipy.util.prompt_for_user_token(
        username=config.SPOTIFY['NAME'],
        scope=config.SPOTIFY['SCOPE'],
        client_id=config.SPOTIFY['ID'],
        client_secret=config.SPOTIFY['HASH'],
        redirect_uri=config.SPOTIFY['REDIRECT'],
        cache_path=get_cache_path(),
        oauth_manager=spotipy.oauth2.SpotifyOAuth(
            username=config.SPOTIFY['NAME'],
            client_id=config.SPOTIFY['ID'],
            client_secret=config.SPOTIFY['HASH'],
            scope=config.SPOTIFY['SCOPE'],
            redirect_uri=config.SPOTIFY['REDIRECT'],
            cache_path=get_cache_path(),
            requests_timeout=10
        )
    )
