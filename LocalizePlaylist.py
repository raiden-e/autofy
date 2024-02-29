import time
import json
import os
import re
import argparse
from os.path import join as join_path

import config
from util import playlist
from util.spotify import get_spotify_client

test = False
# test = True


def main() -> None:
    tracks = data['items']
    preprocess(tracks)

    localize_tracks(tracks)

    lost_tracks, lost_text = [], ""
    for track in tracks:
        if not track['found'] and not track['is_local']:
            lost_tracks.append(track['track']['external_urls']['spotify'])
            lost_text += f"\033[0;96m{track['track']['external_urls']['spotify']} \033[0;37m{track['track']['artists'][0]['name']} - {track['track']['name']}\n"

    print("\nList of lost tracks:")
    print(lost_text)
    print(f"\nLost: {len(lost_tracks)} / {len(tracks)}")

    local_tracks = [x for x in tracks if x['found']]

    if not lost and len(local_tracks) > 0:
        export(local_tracks)

    if test:
        print("Test session, skipping lost tracks playlist")
        return
    if len(lost_tracks) > 1:
        playlist.clear(_sp, config.SPOTIFY['LOSTTRACKS'])
        time.sleep(1)
        playlist.addAsync(_sp, lost_tracks, config.SPOTIFY['LOSTTRACKS'])


def export(pl):
    output = "#EXTM3U\n"
    for tr in pl:
        output += f"#EXTINF:{int(tr['track']['duration_ms']/1000)}, {tr['track']['artists'][0]['name']} - {tr['track']['name']}\n"
        output += "." + str(tr['found']).replace(folder, "") + "\n"

    with open(join_path(folder, get_playlist_name()), 'w', encoding='utf-8') as f:
        f.write(output)


def get_playlist_name():
    if _sp:
        playlist_details = _sp.playlist(playlist_id)
        playlist_re = r"([^\wäöüÄÖÜß\ \.,!\#§%\&\(\)\{\}\[\]\-_\+])|(^\s+)|(\s+$)"
        playlist_name = re.sub(playlist_re, "", playlist_details['name'], re.IGNORECASE)
        playlist_name = re.sub(r"\s{2,}", " ", playlist_name, re.IGNORECASE)
        playlist_name.rstrip()

        if playlist_name == "":
            playlist_name = "new_playlist"
    else:
        playlist_name = "0_test_new_playlist"

    if os.path.exists(join_path(folder, f"{playlist_name}.m3u8")):
        i = 0
        while os.path.exists(join_path(folder, f"{playlist_name}_{i}.m3u8")):
            i += 1
        playlist_name = f"{playlist_name}_{i}"
    return f"{playlist_name}.m3u8"


def escape(inp: str):
    # escape .^$ with "\""
    inp = re.sub(r'([\.\^\$+])', r"\\\1", inp)

    # replace Ø∆├\»()[]-&: with .? (0 or 1 of anything)
    inp = re.sub(r"[\[\]\(\)Ø∆├»\-:']", r".*", inp, re.IGNORECASE)
    inp = re.sub("&", r".*", inp, re.IGNORECASE)
    # \s*, \s+ 2 or more with single \s*
    inp = re.sub(r"(?:\\s\*?){2,}|\s+|(?:\\s(?:\*|\+)?){2,}", r"\\s*", inp, re.IGNORECASE)
    return inp


def escape_title(inp: str):
    # Krl Mx - Holy Gucci (Clair Remix) -> Krl.*Mx.*Holy.*Gucci.*Clair.*Remix.*
    inp = re.sub(r"\(?(?:(?:feat|with|ft)\.?)+\s*\)?", "", inp, re.IGNORECASE)
    # remove " - (Deluxe, Radio, Original) (Edition, Edit, Mix, Version)"
    inp = re.sub(r"(?:\s*-\s*)?\(?:?(?:Deluxe|Radio|Original).?(?:Edition|Edit|Mix|Version)\)?", "", inp, re.IGNORECASE)
    # remove slowed, "bass boosted"
    inp = re.sub(r"slowed\s+(?:\+|and|&)*reverb(?:ed)?", r"", inp, re.IGNORECASE)
    forbiddenPhases = (
        "Re-?Recorded",
        "Remastered",
        r"Bass\s*Boosted",
        "Official",
        "Extended"
    )
    for phase in forbiddenPhases:
        inp = re.sub(phase, r"", inp, re.IGNORECASE)
    inp = re.sub(r"\s", r"\\s*", inp, re.IGNORECASE)
    inp = re.sub(r"(?:\\s(?:\*|\+|\?)?){2,}", r"\\s*", inp, re.IGNORECASE)
    return escape(inp)


def localize_tracks(tracks):
    music_extensions = tuple(['.mp3', '.m4a', '.flac', '.wav', '.ogg'])
    for root, _, files in os.walk(folder):
        print('\r' + root, end='')
        for file in files:
            if file.endswith(music_extensions):
                insert_track(tracks, root, file)
    return tracks


def preprocess(tracks):
    remove = []
    for track in tracks:
        if track['is_local']:
            remove.append(track)
            continue


        tr = track['track']
        track['reMatch'] = escape_title(tr['name'])
        track['artistsRe'] = r"(?:" + "|".join([re.escape(x["name"]) for x in tr['artists']]) + r")"
        track['found'] = False
    for track in remove:
        tracks.remove(track)


def insert_track(tracks, root, file):
    for track in tracks:
        if not track['found']:
            if re.search(track['reMatch'], file, re.IGNORECASE):
                if re.search(track['artistsRe'], file, re.IGNORECASE):
                    track['found'] = join_path(root, file)
                    print(
                        f"Found: {track['track']['artists'][0]['name']} - {track['track']['name']} | {file.replace(folder, '')}")
                    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--playlistid')
    parser.add_argument('-f', '--folder')
    parser.add_argument('-l', dest='lost', action='store_true')
    parser.add_argument('-s', dest='single', action='store_true')
    parser.add_argument('-t', dest='test', action='store_true')
    args = parser.parse_args()

    if not playlist.verify_url(args.playlistid):
        raise AttributeError("Please enter a valid url")
    if not os.path.exists(args.folder):
        raise AttributeError("Please enter a valid folder")

    playlist_id = args.playlistid
    folder = args.folder
    lost = args.lost

    _sp = get_spotify_client()
    if args.test:
        try:
            with open('response.json', mode='r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = playlist.getAsync(_sp, playlist_id, publicOnly=True)
        _sp = False
    else:
        data = playlist.getAsync(_sp, playlist_id, publicOnly=True)

    main()
