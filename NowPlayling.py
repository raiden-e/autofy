import argparse
import os
import time
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union

import requests
from PIL import Image

from util.spotify import get_spotify_client
import spotipy
from spotipy.exceptions import SpotifyOauthError

BASE_DIR = Path(__file__).resolve().parent

if os.name == 'nt':
    import ctypes.wintypes


def get_docs_folder() -> Path:
    if os.name != 'nt':
        target = BASE_DIR / 'util'
        target.mkdir(parents=True, exist_ok=True)
        return target

    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return Path(buf.value)


def get_media_folder() -> Path:
    appdata = os.getenv('APPDATA')
    if appdata:
        base = Path(appdata)
    else:
        base = Path.home() / 'Library' / 'Application Support'

    folder = base / 'autofy' / 'Media'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


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


def main(interval: float = 4.0, max_loops: Optional[int] = None, duration: Optional[float] = None):
    interval = max(interval, 0.1)
    path = get_docs_folder()
    print(f"Writing to: {path}")
    _spotify = get_spotify_client()
    old_id = False
    loops = 0
    started = time.monotonic()

    while True:
        if max_loops is not None and loops >= max_loops:
            print(f"Reached loop limit ({max_loops}). Exiting.")
            break
        if duration is not None and (time.monotonic() - started) >= duration:
            print(f"Reached duration limit ({duration}s). Exiting.")
            break

        time.sleep(interval)
        try:
            playback = _spotify.current_playback()
        except SpotifyOauthError as e:
            # Common cause: refresh token revoked or invalid. Provide clear remediation.
            print("Spotify OAuth error:", e)
            print("This usually means the stored refresh token was revoked. To fix: \n"
                  "  1) Delete the cache file: './util/spotify.cache'\n"
                  "  2) Re-run this script to re-authorize (a browser window will open).\n"
                  "Alternatively, run the `get_new_token()` helper in `util/spotify.py` to initiate re-auth.")
            return
        if playback is None or not playback["is_playing"]:
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
        for key, value in texts.items():
            try_write(str(path / key), value)

        folder = get_media_folder()
        pics = list(folder.glob('*-SpotifyNP.jpg'))
        snp_pic = "SpotifyNP.jpg" if len(pics) == 0 else pics[0]

        get_np_pic(
            playback['item']['album']['images'][0]['url'],
            str(folder / snp_pic)
        )

        print(f"{playback['item']['id']}\n{full_text}")
        loops += 1


def parse_args():
    parser = argparse.ArgumentParser(description="Write the current Spotify track info to text/image files.")
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single playback check and exit."
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_args()
    loops = 1 if cli_args.once else None
    main(max_loops=loops)
