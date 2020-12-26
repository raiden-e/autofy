import ctypes.wintypes
import os
import time
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

import requests
import spotipy
from PIL import Image

from util.spotify import get_spotify_client


def get_docs_folder():
    if not os.name == 'nt':
        return "/user/docs/"
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value


def get_np_pic(url, path: Union[str, Path, BinaryIO]):
    response = requests.get(url)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with Image.open(BytesIO(response.content)) as pic:
        pic.save(path)


def now_playing(_spotify: spotipy.Spotify, path: str, old_id=None):
    if not _spotify:
        raise TypeError(spotipy.Spotify)
    if not path:
        raise TypeError(str)
    playback = _spotify.current_playback()
    if playback and playback["is_playing"]:
        if old_id:
            new_id = playback["item"]["id"]
            if new_id == old_id:
                return (playback["item"]["id"], "Same Song ")

        old_id = playback["item"]["id"]
        playback_text = (
            f"{playback['item']['artists'][0]['name']} - "
            f"{playback['item']['name']} | Album: "
            f"{playback['item']['album']['name']}"
        )

        with open(os.path.join(path, 'SpotifyNP.txt'), 'w') as f:
            f.write(playback_text)
        with open(os.path.join(path, 'SpotifyNPTitle.txt'), 'w') as f:
            f.write(playback['item']['name'])
        with open(os.path.join(path, 'SpotifyNPartist.txt'), 'w') as f:
            f.write(playback['item']['artists'][0]['name'])

        get_np_pic(
            playback['item']['album']['images'][0]['url'],
            os.path.join(
                os.getenv('APPDATA'),
                'slobs-client', 'Media', '505581849-SpotifyNP.jpg'
            )
        )

        return [playback["item"]["id"], f"\n{playback_text}"]

    else:
        return (None, "Not playing")


def main(repeat=True):
    path = get_docs_folder()
    _spotify = get_spotify_client()
    result = now_playing(_spotify, path)
    print(result[1])
    while repeat:
        time.sleep(4)
        result = now_playing(_spotify, path, result[0])
        print(result[1], end="")


if __name__ == "__main__":
    main()
