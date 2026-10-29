""" Localize Spotify playlist tracks

Searches for tracks in the playlist, that are missing in a specified dir.

Usage:
  python LocalizePlaylist.py -p <playlist_url> -f <folder_path> [-l] [-s] [-t]
Options:
    -p, --playlistid   Spotify playlist URL to localize
    -f, --folder       Path to the folder containing local music files
    -l, --lost         If set, creates/updates a Spotify playlist with tracks that were not found locally
    -s, --single       If set, only processes the first track in the playlist (useful for testing)
    -t, --test         If set, runs in test mode using 'response.json' instead of making API calls (for development/testing purposes)
"""

import time
import json
import os
import re
import string
import argparse
import unicodedata
from os.path import join as join_path

import config
from util import playlist
from util.spotify import get_spotify_client

# Map every punctuation character to a space in one pass (see normalize_string).
_PUNCT_TABLE = str.maketrans({p: " " for p in string.punctuation})

# Descriptive words stripped from titles/filenames before matching.
_BANNED_WORDS = {
    "feat", "ft", "with", "deluxe", "radio", "original", "edition", "edit",
    "mix", "version", "remastered", "official", "extended",
}

def main() -> None:
    tracks = data["items"]
    preprocess(tracks)

    if single:
        tracks[:] = tracks[:1]

    localize_tracks(tracks)

    lost_tracks, lost_text = [], ""
    for track in tracks:
        if not track["found"] and not track["is_local"]:
            lost_tracks.append(track["track"]["external_urls"]["spotify"])
            lost_text += f"\033[0;96m{track['track']['external_urls']['spotify']} \033[0;37m{track['track']['artists'][0]['name']} - {track['track']['name']}\n"

    print("\nList of lost tracks:")
    print(lost_text)
    print(f"\nLost: {len(lost_tracks)} / {len(tracks)}")

    local_tracks = [x for x in tracks if x["found"]]

    if not lost and len(local_tracks) > 0:
        export(local_tracks)

    if test:
        print("Test session, skipping lost tracks playlist")
        return
    if len(lost_tracks) > 1:
        playlist.clear(_sp, config.SPOTIFY["LOSTTRACKS"])
        time.sleep(1)
        playlist.addAsync(_sp, lost_tracks, config.SPOTIFY["LOSTTRACKS"])


def export(pl):
    output = "#EXTM3U\n"
    for tr in pl:
        output += f"#EXTINF:{int(tr['track']['duration_ms']/1000)}, {tr['track']['artists'][0]['name']} - {tr['track']['name']}\n"
        output += "./" + os.path.relpath(tr["found"], folder) + "\n"

    with open(join_path(folder, get_playlist_name()), "w", encoding="utf-8") as f:
        f.write(output)


def get_playlist_name():
    if _sp:
        playlist_details = _sp.playlist(playlist_id)
        playlist_re = r"([^\wäöüÄÖÜß\ \.,!\#§%\&\(\)\{\}\[\]\-_\+])|(^\s+)|(\s+$)"
        playlist_name = re.sub(playlist_re, "", playlist_details["name"], flags=re.IGNORECASE)
        playlist_name = re.sub(r"\s{2,}", " ", playlist_name, flags=re.IGNORECASE)

        if playlist_name == "":
            playlist_name = "new_playlist"
    else:
        playlist_name = "0_test_new_playlist"

    candidate = f"{playlist_name}.m3u8"
    i = 0
    while os.path.exists(join_path(folder, candidate)):
        candidate = f"{playlist_name}_{i}.m3u8"
        i += 1
    return candidate


def normalize_string(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.translate(_PUNCT_TABLE)
    return {w for w in s.split() if w not in _BANNED_WORDS}


def build_index(tracks):
    """Build an inverted index mapping a title anchor word to candidate tracks.

    A track can only match a file if every word of its title is present in the
    file name, so it suffices to look at files that contain one chosen anchor
    word (the rarest title word) rather than scanning every track per file.

    Tracks whose title normalizes to an empty set have no anchor word and match
    on artist alone; they are returned separately so they can be checked against
    every file. Each track keeps its original playlist index in "order" so the
    per-file "first unfound track wins" ordering is preserved.
    """
    word_freq = {}
    for track in tracks:
        for w in track["search_title"]:
            word_freq[w] = word_freq.get(w, 0) + 1

    index = {}
    no_anchor = []
    for i, track in enumerate(tracks):
        track["order"] = i
        title = track["search_title"]
        if not title:
            no_anchor.append(track)
            continue
        anchor = min(title, key=lambda w: word_freq[w])
        index.setdefault(anchor, []).append(track)

    return index, no_anchor


def localize_tracks(tracks):
    music_extensions = (".mp3", ".m4a", ".flac", ".wav", ".ogg")
    index, no_anchor = build_index(tracks)
    for root, _, files in os.walk(folder):
        # \033[K clears the rest of the line so shorter paths don't leave a
        # trailing fragment from a previous, longer path.
        print(f"\r\033[K{root}", end="", flush=True)
        for file in files:
            if file.endswith(music_extensions):
                insert_track(index, no_anchor, root, file)
    print("\r\033[K", end="")
    return tracks


def preprocess(tracks):
    for track in list(tracks):
        if track["is_local"]:
            tracks.remove(track)
            continue

        tr = track["track"]
        track["search_title"] = normalize_string(tr["name"])
        track["search_artists"] = [normalize_string(x["name"]) for x in tr["artists"]]
        track["found"] = False


def insert_track(index, no_anchor, root, file):
    file_norm = normalize_string(file)

    # Only tracks whose anchor word appears in the file can match; add the
    # anchorless tracks (title matched on artist alone) so behavior is identical
    # to scanning every track.
    candidates = list(no_anchor)
    for word in file_norm:
        if word in index:
            candidates.extend(index[word])

    # Preserve the original per-file "first unfound track in playlist order wins".
    candidates.sort(key=lambda t: t["order"])

    for track in candidates:
        if track["found"]:
            continue
        if not track["search_title"].issubset(file_norm):
            continue
        if not any(a.issubset(file_norm) for a in track["search_artists"]):
            continue

        found_path = join_path(root, file)
        track["found"] = found_path
        rel = os.path.relpath(found_path, folder)
        # \r\033[K clears the in-progress directory line so this prints clean.
        print(f"\r\033[KFound: {track['track']['artists'][0]['name']} - {track['track']['name']} | {rel}")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--playlistid")
    parser.add_argument("-f", "--folder")
    parser.add_argument("-l", dest="lost", action="store_true")
    parser.add_argument("-s", dest="single", action="store_true")
    parser.add_argument("-t", dest="test", action="store_true")
    args = parser.parse_args()

    if not args.playlistid or not playlist.verify_url(args.playlistid):
        raise AttributeError("Please enter a valid url")
    folder = os.path.expanduser(args.folder) if args.folder else None
    if not folder or not os.path.isdir(folder):
        raise AttributeError("Please enter a valid folder")

    playlist_id = args.playlistid
    lost = args.lost
    single = args.single
    test = args.test

    _sp = get_spotify_client()
    if args.test:
        try:
            with open("response.json", mode="r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = playlist.getAsync(_sp, playlist_id, publicOnly=True)
        _sp = False
    else:
        data = playlist.getAsync(_sp, playlist_id, publicOnly=True)

    main()
