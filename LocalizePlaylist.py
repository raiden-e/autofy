import json
import os
import re
import sys
# import spotipy
# import pprint


def main(folder) -> None:
    def escape(inp: str):
        for char in ('.', ' ', '(', ')', '[', ']', '{', '}', '^', '$', '+'):
            inp = inp.replace(char, '\\' + char)
        for char in ('"', "'", "├»"):
            inp = inp.replace(char, ".?")
        return inp

    def find_relative(tr, folder):
        # match at least one artist
        re_match = f".?({escape(tr['artists'][0]['name'])}"
        if len(tr['artists']) > 1:
            for artist in tr['artists'][1:]:
                re_match += f"|{escape(artist['name'])}"

        # add a "-" symbol
        re_match += ")+.?\\ *-\\ *.?"
        re_match += escape(tr['name'])
        re_match += ".?"

        for root, _, files in os.walk(folder):
            # pprint.pp((root, dirs, files))
            print(root)
            for file in files:
                if file[-4:] in ('.mp3', '.m4a', 'flac', '.wav', '.ogg'):
                    if re.match(re_match, file):
                        return os.path.join(f"{root}\\{file}")
        return False

    def export(pl, folder, playlist_file):
        output = "#EXTM3U\n"
        for tr in pl:
            output += f"#EXTINF:{int(tr[1]['duration_ms']/1000)}, {tr[1]['artists'][0]['name']} - {tr[1]['name']}\n"
            output += "." + str(tr[0]).replace(folder, "") + "\n"

        with open(playlist_file, 'w', encoding='utf-8') as f:
            f.write(output)

    with open('response.json', mode='r', encoding='utf-8') as f:
        data = json.load(f)

    tracks = data['tracks']['items']
    playlist = []
    for track in tracks:
        print(f"=== Searching {track['track']['name']} ===")
        rel_dir = find_relative(track['track'], folder)
        if rel_dir:
            playlist.append([rel_dir, track['track']])

    export(playlist, folder, os.path.join(folder, "new_playlist.m3u8"))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.curdir)
