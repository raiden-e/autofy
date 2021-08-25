import ctypes.wintypes
import os
import time
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

import requests
from PIL import Image

from util.spotify import get_spotify_client


def get_docs_folder():
    if os.name != 'nt':
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


def try_write(file: str, text: str):
    try:
        with open(file, 'w', encoding='utf-8-sig') as f:
            f.write(text)
            print(f"Wrote: {file}")
    except Exception as e:
        print(f"Couldnt write {file}\n{e}")


def main(repeat=True):
    path = get_docs_folder()
    print(f"Writing to: {path}")
    _spotify = get_spotify_client()
    old_id = False

    while repeat:
        time.sleep(4)
        playback = _spotify.current_playback()
        if not playback["is_playing"]:
            print("Playback stopped", end=None)
            continue

        if playback["item"]["id"] == old_id:
            print("Same Song -", playback["item"]["id"])
            continue

        old_id = playback["item"]["id"]

        full_text = f"{playback['item']['artists'][0]['name']} - {playback['item']['name']} | Album: {playback['item']['album']['name']}"
        texts = {
            'SpotifyNP.txt': full_text,
            'SpotifyNPTitle.txt': playback['item']['name'],
            'SpotifyNPartist.txt': playback['item']['artists'][0]['name'],
        }
        for key in texts:
            try_write(os.path.join(path, key), texts[key])

        folder = os.path.join(os.getenv('APPDATA'), 'slobs-client', 'Media')
        pics = [x for x in Path(folder).glob('*-SpotifyNP.jpg')]
        snp_pic = "SpotifyNP.jpg" if len(pics) == 0 else pics[0]

        get_np_pic(
            playback['item']['album']['images'][0]['url'],
            os.path.join(folder, snp_pic)
        )

        print(f"{playback['item']['id']}\n{full_text}")


if __name__ == "__main__":
    main()
