import time
import json
import os
import re
import sys
from os.path import join as ojoin

import config
from util import playlist
from util.spotify import get_spotify_client

test = False
# test = True


def main(pl) -> None:
    escapes = [re.compile(r'([\.\^\$+])'),
               re.compile(r"[\"\'(\├\»)\(\)\[\]\-\&\:]"),
               re.compile(r"(\\s\*?){2,}|\s+|(\\s(\*|\+)?){2,}"),]

    def escape(inp: str):
        inp = re.sub(escapes[0], r"\\\1", inp)
        inp = re.sub(escapes[1], r".?", inp)
        inp = re.sub(escapes[2], r"\\s*", inp)
        return inp

    def export(pl):
        output = "#EXTM3U\n"
        for tr in pl:
            output += f"#EXTINF:{int(tr[1]['duration_ms']/1000)}, {tr[1]['artists'][0]['name']} - {tr[1]['name']}\n"
            output += "." + str(tr[0]).replace(folder, "") + "\n"

        with open(ojoin(folder, get_playlist_name()), 'w', encoding='utf-8') as f:
            f.write(output)

    def get_playlist_name():
        if _sp:
            playlist_details = _sp.playlist(pl)
            playlist_re = r"([^\wäöüÄÖÜß\ \.,!\#§%\&\(\)\{\}\[\]\-_\+])|(^\s+)|(\s+$)"
            playlist_name = re.sub(playlist_re, "", playlist_details['name'])
            playlist_name = re.sub(r"\s{2,}", " ", playlist_name)

            if playlist_name == "":
                playlist_name = "new_playlist"
        else:
            playlist_name = "0_test_new_playlist"

        if os.path.exists(ojoin(folder, f"{playlist_name}.m3u8")):
            i = 0
            while os.path.exists(ojoin(folder, f"{playlist_name}_{i}.m3u8")):
                i += 1
            playlist_name = f"{playlist_name}_{i}"
        return f"{playlist_name}.m3u8"

    if test:
        _sp = False
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
        re_artists = [escape(artist['name']) for artist in tr['artists']]
        re_match = f".?({'|'.join(re_artists)})+"

        # add a "-" symbol
        re_match += r".?\s*-\s*.?"
        re_track_name = escape(tr['name'])
        # minus = '-'
        V_I_P = re.search(r"\s*[-\(\[\{]?\s*VIP\s*[\)\]\}]?", tr['name'])
        # V - I - P!
        if V_I_P:
            VIP_match = tr['name'][0:V_I_P.span()[0]] + tr['name'][V_I_P.span()[1]:]
            re_track_name = "|".join((re_track_name, escape(VIP_match)))

        track['reMatch'] = f"{re_match}({re_track_name}).?"
        track['found'] = False

    local_tracks = []
    for root, _, files in os.walk(folder):
        print(root)
        for file in files:
            if file[-4:] in ('.mp3', '.m4a', 'flac', '.wav', '.ogg'):
                for track in tracks:
                    if not track['found'] and re.findall(track['reMatch'], file, re.IGNORECASE):
                        track['found'] = True
                        local_tracks.append([ojoin(f"{root}\\{file}"), track['track']])
                        break

    lost_tracks = []
    lost_text = ""
    lost_urls = ""
    for track in tracks:
        if not track['found'] and not track['is_local']:
            lost_tracks.append(track['track']['external_urls']['spotify'])
            lost_urls += str(lost_tracks[-1]) + "\n"
            lost_text += f"{track['track']['artists'][0]['name']} - {track['track']['name']}\n"

    print("\nList of lost tracks:")
    print(lost_text)
    print(lost_urls)

    export(local_tracks)

    if test:
        print("Test sessison, skipping lost tracks")
        return
    if len(lost_tracks) > 1:
        playlist.clear(_sp, config.LOSTTRACKS)
        time.sleep(1)
        playlist.addAsync(_sp, lost_tracks, config.LOSTTRACKS)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: LocalizePlaylist.py <music folder> <spotify link>")
        sys.exit()
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
