import base64
import os

from util import gist
from util.spotify import get_spotify_client


def main():
    _spotify = get_spotify_client()
    playlist_id = '57VYcWAMIc97Ig41vPpev6'
    gist_name = "autofy.json"

    pic_path = os.path.join('util', 'cover.jpg')

    backup = gist.load(gist_name)
    backup['report_count'] = int(backup['report_count']) + 1 if ('report_count' in backup) else 1

    description = f'"My playlist got reported like {backup["report_count"]} times now, which is really wicked 🔥" -raiden_e'

    _spotify.playlist_change_details(
        playlist_id, name="Hard DnB 🔥 Drum and Bass", description=description)

    with open(pic_path, "rb") as pic:
        # Make sure the image size does not exceed 256 kb or so
        _spotify.playlist_upload_cover_image(
            f"spotify:playlist:{playlist_id}", base64.b64encode(pic.read()))

    gist.update(gist_name, backup, description)


if __name__ == '__main__':
    main()
