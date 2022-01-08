import json
import os
import re
import sys
from os.path import join as ojoin

from util import playlist
from util.spotify import get_spotify_client

test = False
# test = True


def main(pl) -> None:
    def escape(inp: str):
        for char in ('.', ' ', '(', ')', '[', ']', '{', '}', '^', '$', '+'):
            inp = inp.replace(char, '\\' + char)
        for char in ('"', "'", "├»"):
            inp = inp.replace(char, ".?")
        return inp

    def export(pl):
        output = "#EXTM3U\n"
        for tr in pl:
            output += f"#EXTINF:{int(tr[1]['duration_ms']/1000)}, {tr[1]['artists'][0]['name']} - {tr[1]['name']}\n"
            output += "." + str(tr[0]).replace(folder, "") + "\n"

        with open(ojoin(folder, get_playlist_name()), 'w', encoding='utf-8') as f:
            f.write(output)

    def get_playlist_name():
        playlist_details = _sp.playlist(pl)
        playlist_name = playlist_details['name']
        for char in playlist_details['name']:
            if not re.match(r"[a-zA-Z0-9äöüÄÖÜß\.§%&(){}\[\]-_\+]", char):
                playlist_name.replace(char, "")

        if playlist_name == "":
            playlist_name = "new_playlist"

        if os.path.exists(ojoin(folder, f"{playlist_name}.m3u8")):
            i = 0
            while os.path.exists(ojoin(folder, f"{playlist_name}_{i}.m3u8")):
                i += 1
            playlist_name = f"{playlist_name}_{i}"
        return f"{playlist_name}.m3u8"

    def find_match(root, file, inp):
        for track in inp:
            if re.match(track['reMatch'], file):
                local_tracks.append([ojoin(f"{root}\\{file}"), track['track']])
                return

    if test:
        with open('response.json', mode='r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        _sp = get_spotify_client()
        data = playlist.getAsync(_sp, pl, publicOnly=True)

    tracks = data['items']

    # preprocessing
    for track in tracks:
        # match at least one artist
        tr = track['track']
        re_match = f".?({escape(tr['artists'][0]['name'])}"
        if len(tr['artists']) > 1:
            for artist in tr['artists'][1:]:
                re_match += f"|{escape(artist['name'])}"

        # add a "-" symbol
        track['reMatch'] = f"{re_match})+.?\\ *-\\ *.?{escape(tr['name'])}.?"

    local_tracks = []
    for root, _, files in os.walk(folder):
        # pprint.pp((root, dirs, files))
        print(root)
        for file in files:
            if file[-4:] in ('.mp3', '.m4a', 'flac', '.wav', '.ogg'):
                find_match(root, file, tracks)

    export(local_tracks)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        playlist_id = input("Please enter the link to the playlist: ")
    else:
        playlist_id = sys.argv[2]
    if not playlist.verify_url(playlist_id):
        raise AttributeError("Please enter a valid url")

    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        print("WARNING: Using <os.curdir> as folder")
        folder = os.curdir

    main(playlist_id)
