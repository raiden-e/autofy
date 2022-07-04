import base64
import concurrent.futures
import datetime
import math
import re
from time import strftime

import spotipy
from spotipy.exceptions import SpotifyException


def get(_spotify: spotipy.Spotify, playlistId: str, publicOnly=False) -> dict:
    result = _spotify.playlist_items(playlist_id=playlistId)

    while result['next']:
        tmp = _spotify.next(result)
        result['items'].extend(tmp['items'])
        result['next'] = tmp['next']

    if publicOnly:
        result['items'] = [item for item in result['items'] if not item['is_local']]

    return result


def getAsync(_spotify: spotipy.Spotify, playlistId: str, publicOnly=False) -> dict:
    result = _spotify.playlist_tracks(playlistId)
    if result['total'] <= 100:
        return result

    offsets = [i * 100 for i in get_TaskCount(result['total'], True)]
    exec_results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for offset in offsets:
            exec_results.append(
                executor.submit(
                    _spotify.playlist_tracks,
                    playlistId,
                    None,
                    100,
                    offset
                ))

        executor_results = [f.result()["items"]
                            for f in concurrent.futures.as_completed(exec_results)]

    if publicOnly:
        for x in executor_results:
            for y in x:
                if y["track"] is not None and not y["is_local"]:
                    result["items"].append(y)
    else:
        for x in executor_results:
            for y in x:
                if y["track"] is not None:
                    result["items"].append(y)

    return result


def add(_spotify: spotipy.Spotify, tracks_to_add: list, playlistId: str):
    if not _spotify:
        raise Exception("_spotify has to be parsed!")
    if not tracks_to_add:
        raise Exception("tracks_to_add has to be parsed!")

    for j in get_TaskCount(len(tracks_to_add)):
        _spotify.playlist_add_items(
            playlist_id=playlistId,
            items=tracks_to_add[(j*100):((j+1)*100)]
        )


def addAsync(_spotify: spotipy.Spotify, tracks_to_add: list, playlistId: str):
    if not _spotify:
        raise Exception("_spotify has to be parsed!")
    if not tracks_to_add:
        raise Exception("tracks_to_add has to be parsed!")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for j in get_TaskCount(len(tracks_to_add)):
            executor.submit(
                _spotify.playlist_add_items,
                playlistId,
                tracks_to_add[(j*100):((j+1)*100)])


def new_playlist(_spotify: spotipy.Spotify, tracks_to_add: list, name: str, pic: str = None):
    x = _spotify.user_playlist_create(
        _spotify.me()['id'],
        name,
        description=f"Backup since {strftime('%d')} {strftime('%b')} {strftime('%Y')}"
    )

    if pic is not None:
        try:
            with open(pic, "rb") as p:
                _spotify.playlist_upload_cover_image(x["id"], base64.b64encode(p.read()))
        except (FileExistsError, FileNotFoundError):
            print(f"[WARNING]: Could not find picture: {pic}\n  Skipping image upload")
        except SpotifyException as e:
            print(
                f"[WARNING]: Could not upload picture: {pic}\n  Skipping image upload\n  Trace:\n{e.with_traceback(None)}")

    if len(tracks_to_add) > 0:
        if len(tracks_to_add) > 100:
            addAsync(_spotify, tracks_to_add, x["id"])
            return x
        add(_spotify, tracks_to_add, x["id"])
    return x


def get_TaskCount(x, start_at_1=False) -> range:
    # Spotify's API wont allow more than 100 songs per POST:
    # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/#body-parameters:~:text=A%20maximum%20of%20100

    return range(1 if start_at_1 else 0, int(math.ceil(x / 100.0)))


def clear(_spotify: spotipy.Spotify, playlistId: str):
    tracks = []
    for x in getAsync(_spotify, playlistId)['items']:
        if not x["is_local"]:
            tracks.append(x["track"]["uri"])

    for i in get_TaskCount(len(tracks)):
        _spotify.playlist_remove_all_occurrences_of_items(
            playlist_id=playlistId,
            items=tracks[(i*100):((i+1)*100)]
        )


def edited_this_week(_spotify: spotipy.Spotify, playlist_id: str) -> bool:
    try:
        lastEditStr = _spotify.playlist_tracks(playlist_id, limit=10)["items"]
        newest_track = lastEditStr[0]
        for item in lastEditStr[1:]:
            if item['added_at'] > newest_track['added_at']:
                newest_track = item
        lastEditStr = newest_track['added_at']
        l = datetime.datetime.strptime(lastEditStr, '%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        print("LoFi playlist was empty...")
        return False

    d = datetime.datetime.now()

    datetime_current = int(f"{d.year}{d.strftime('%W')}")
    datetime_lastEdit = int(f"{l.year}{l.strftime('%W')}")

    print(f"{'Current Week:':<16}{datetime_current}")
    print(f"{'Last edit:':<16}{datetime_lastEdit}")

    if datetime_current > datetime_lastEdit:
        print("continuing")
        return False
    return True


def deduplify_list(main_list: list, base_list: list, ignore: list) -> list:
    def track_to_seen(track):
        return {
            "name": track['name'],
            "artists": [artist['name'] for artist in track['artists']],
            "duration": track['duration_ms'],
            "id": track['id'],
        }

    def print_diff(a, b):
        art_a, art_b = f"{a['artists'][0]['name']}", f"{b['artists'][0]}"
        for artist_a, artist_b in zip(a['artists'][1:], b["artists"][1:]):
            art_a += f", {artist_a['name']}"
            art_b += f", {artist_b}"
        print("  Duplicate Meta:")
        print(f"    {a['id']}  {a['name']}{' ':>30}| {art_a}")
        print(f"    {b['id']}  {b['name']}{' ':>30}| {art_b}")

    def inner(xt):
        for y in seen_tracks:
            if xt["id"] == y["id"]:
                print(f"  Duplicate ID: {y['name']:40}{xt['id']}|{y['id']}")
                return False

        for y in seen_tracks:
            if xt["name"] == y["name"]:
                if abs(y["duration"] - xt["duration_ms"]) <= 100:  # if duration somewhat same
                    for artist in xt["artists"]:
                        if artist['name'] in y["artists"]:
                            print_diff(xt, y)
                            return False
        return True

    seen_tracks = [track_to_seen(track['track']) for track in base_list + ignore]

    new_main = []

    for x in main_list:
        xt = x['track']
        if inner(xt):
            new_main.append(x)
        seen_tracks.append(track_to_seen(xt))

    return new_main


def verify_url(url: str):
    if not isinstance(url, str):
        raise AttributeError("Parameter is not of type str")
    url = url.strip()
    if re.match(r'^[a-zA-Z0-9]{22}$', url):
        return True
    if re.match(r'^(https?:\/\/){0,1}open\.spotify\.com\/playlist\/[a-zA-Z0-9]{22}', url):
        return True
    if re.match(r'^spotify:playlist:([a-zA-Z0-9]{22})$', url):
        return True
    return False
