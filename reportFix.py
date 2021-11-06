import base64
import json
import os

from util import gist
from util.spotify import get_spotify_client


def main():
    _spotify = get_spotify_client()
    id = '57VYcWAMIc97Ig41vPpev6'
    gist_name = "autofy.json"

    pic_path = os.path.join('util', 'cover.jpg')

    backup = gist.load(gist_name)
    report_count = int(backup['report_count']) + 1 if ('report_count' in backup) else 1
    description = f'"My playlist got reported like {report_count} times now, which is really wicked 🔥" -raiden_e'

    _spotify.playlist_change_details(id, name="Hard DnB 🔥 Drum and Bass", description=description)

    with open(pic_path, "rb") as pic:
        # Make sure the image size does not exceed 256 kb or so
        _spotify.playlist_upload_cover_image(f"spotify:playlist:{id}", base64.b64encode(pic.read()))

    gist.update(gist_name, json.dumps(backup), description)


if __name__ == '__main__':
    main()
