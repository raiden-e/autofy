import base64
import concurrent.futures
import datetime
import math
import re
import time
from time import strftime

import spotipy
from spotipy.exceptions import SpotifyException


def get(_spotify: spotipy.Spotify, playlistId: str, publicOnly=False) -> dict:
    result = _spotify.playlist_items(playlist_id=playlistId)

    while result["next"]:
        tmp = _spotify.next(result)
        result["items"].extend(tmp["items"])
        result["next"] = tmp["next"]

    if publicOnly:
        result["items"] = [item for item in result["items"] if not item["is_local"]]

    return result


def getAsync(_spotify: spotipy.Spotify, playlistId: str, publicOnly=False) -> dict:
    result = _spotify.playlist_tracks(playlistId)
    if result["total"] <= 100:
        return result

    offsets = [i * 100 for i in get_TaskCount(result["total"], True)]
    exec_results = []

    # Use a smaller number of workers to avoid rate limiting
    max_workers = min(5, len(offsets))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, offset in enumerate(offsets):
            # Add a small delay between submissions to avoid rate limiting
            if i > 0:
                time.sleep(0.1)
            exec_results.append(executor.submit(_spotify.playlist_tracks, playlistId, None, 100, offset))

        executor_results = [f.result()["items"] for f in concurrent.futures.as_completed(exec_results)]

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

    for j in get_TaskCount(len(tracks_to_add), item_amount=100):
        _spotify.playlist_add_items(playlist_id=playlistId, items=tracks_to_add[(j * 100) : ((j + 1) * 100)])


def addAsync(_spotify: spotipy.Spotify, tracks_to_add: list, playlistId: str):
    if not _spotify:
        raise Exception("_spotify has to be parsed!")
    if not tracks_to_add:
        raise Exception("tracks_to_add has to be parsed!")

    tasks = list(get_TaskCount(len(tracks_to_add), item_amount=100))
    max_workers = min(5, len(tasks))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, j in enumerate(tasks):
            # Add a small delay between submissions to avoid rate limiting
            if i > 0:
                time.sleep(0.1)
            executor.submit(_spotify.playlist_add_items, playlistId, tracks_to_add[(j * 100) : ((j + 1) * 100)])


def new_playlist(_spotify: spotipy.Spotify, tracks_to_add: list, name: str, pic: str = None):
    x = _spotify.user_playlist_create(
        _spotify.me()["id"], name, description=f"Backup since {strftime('%d')} {strftime('%b')} {strftime('%Y')}"
    )

    if pic is not None:
        try:
            with open(pic, "rb") as p:
                _spotify.playlist_upload_cover_image(x["id"], base64.b64encode(p.read()))
        except (FileExistsError, FileNotFoundError):
            print(f"[WARNING]: Could not find picture: {pic}\n  Skipping image upload")
        except SpotifyException as e:
            print(
                f"[WARNING]: Could not upload picture: {pic}\n  Skipping image upload\n  Trace:\n{e.with_traceback(None)}"
            )

    if len(tracks_to_add) > 0:
        if len(tracks_to_add) > 100:
            addAsync(_spotify, tracks_to_add, x["id"])
            return x
        add(_spotify, tracks_to_add, x["id"])
    return x


def get_TaskCount(x, start_at_1=False, item_amount=50) -> range:
    # Spotify's API wont allow more than 100 songs per POST:
    # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/#body-parameters:~:text=A%20maximum%20of%20100

    if item_amount > 100:
        raise AttributeError(">100 seems like a lot")
    return range(1 if start_at_1 else 0, int(math.ceil(x / item_amount)))


def clear(_spotify: spotipy.Spotify, playlistId: str):
    tracks = []
    for x in getAsync(_spotify, playlistId)["items"]:
        if not x["is_local"]:
            tracks.append(x["track"]["uri"])

    for i in get_TaskCount(len(tracks), item_amount=100):
        _spotify.playlist_remove_all_occurrences_of_items(
            playlist_id=playlistId, items=tracks[(i * 100) : ((i + 1) * 100)]
        )


def edited_this_week(_spotify: spotipy.Spotify, playlist_id: str) -> bool:
    try:
        lastEditStr = _spotify.playlist_tracks(playlist_id, limit=10)["items"]
        newest_track = lastEditStr[0]
        for item in lastEditStr[1:]:
            if item["added_at"] > newest_track["added_at"]:
                newest_track = item
        lastEditStr = newest_track["added_at"]
        l = datetime.datetime.strptime(lastEditStr, "%Y-%m-%dT%H:%M:%SZ")
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
    seen_ids = set()
    seen_metadata = {}

    def add_to_seen(track):
        if not track:
            return
        seen_ids.add(track["id"])
        # Bucket duration to nearest 100ms for fuzzy matching
        duration_bucket = round(track["duration_ms"] / 100)
        key = (track["name"].lower(), frozenset(a["name"].lower() for a in track["artists"]), duration_bucket)
        seen_metadata[key] = track["id"]

    # Pre-populate with base_list and ignore
    for item in base_list + ignore:
        track = item.get("track")
        if track:
            add_to_seen(track)

    new_main = []
    for item in main_list:
        track = item.get("track")
        if not track:
            continue

        if track["id"] in seen_ids:
            continue

        duration_bucket = round(track["duration_ms"] / 100)
        key = (track["name"].lower(), frozenset(a["name"].lower() for a in track["artists"]), duration_bucket)
        if key in seen_metadata:
            continue

        new_main.append(item)
        add_to_seen(track)

    return new_main


def verify_url(url: str):
    if not isinstance(url, str):
        raise AttributeError("Parameter is not of type str")
    url = url.strip()
    # Accepts raw ID, URI, or URL, but only if NOT a Spotify editorial playlist (37i9dQZF1DW...)
    m = re.search(r"([a-zA-Z0-9]{22})", url)
    if not m:
        return False
    playlist_id = m.group(1)
    if playlist_id.startswith("37i9dQZF1D"):
        print("Spotify editorial/algorithmic playlists are not supported.")
        return False
    # Now check if the input is a valid playlist ID, URI, or URL
    if re.match(r"^[a-zA-Z0-9]{22}$", url):
        return True
    if re.match(r"^(https?:\/\/){0,1}open\.spotify\.com\/playlist\/[a-zA-Z0-9]{22}", url):
        return True
    if re.match(r"^spotify:playlist:([a-zA-Z0-9]{22})$", url):
        return True
    return False
