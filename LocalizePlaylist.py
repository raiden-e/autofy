import json
import os
import re
import sys


def main(folder) -> None:
    def find_relative(tr, folder):
        re_match = f"({tr['artists'][0]['name']}"
        if len(tr['artists'] > 1):
            for artist in tr['artists'][1:]:
                re_match += f"|{artist['name']}"

        re_match += ")+.*.*-"
        re_match += str(tr['name'])

        for file in os.walk(folder):

        if re.match(f"{tr}.mp3", file):
            return file.fullname
        return False

    def get_deep_search(track):
        print(track)

    def export(pl, folder, playlist_file):
        output = "#EXTM3U\n"
        for tr in pl:
            output += f"#EXTINF:{tr.no}, {tr.artist} - {tr.title}\n"
            output += str(tr.path.trim(folder))

        with open(playlist_file, 'w', encoding='utf-8') as f:
            f.write(output)

    with open('response.json', mode='r', encoding='utf-8') as f:
        data = json.load(f)

    tracks = data['tracks']['items']
    playlist, deep_search = [], []
    for track in tracks:
        rel_dir = find_relative(track['track'], folder)
        if rel_dir:
            playlist.append(rel_dir)
        else:
            deep_search.append(track)

        if len(deep_search) > 0:
            for tr in deep_search:
                get_deep_search(tr)

    export(playlist, folder, os.path.join(folder, "new_playlist.m3u8"))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.curdir)
