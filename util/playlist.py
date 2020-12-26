import concurrent.futures
import math

import spotipy


def get(
    _spotify: spotipy.Spotify,
    playlistId: str,
    publicOnly=False
) -> dict:

    result = _spotify.playlist_items(playlist_id=playlistId)

    while result['next']:
        tmp = _spotify.next(result)
        result['items'].extend(tmp['items'])
        result['next'] = tmp['next']

    if publicOnly:
        result['items'][:] = [
            item for item in result['items'] if not item.get('is_local')]

    return result


def getAsync(
    _spotify: spotipy.Spotify,
    playlistId: str,
    publicOnly=False
) -> dict:

    result = _spotify.playlist_tracks(playlistId)
    if result['total'] <= 100:
        return result

    executor_results, offsets = [], []

    for i in get_TaskCount(result['total'], True):
        offsets.append(i * 100)

    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        exec_results = [
            executor.submit(
                _spotify.playlist_tracks,
                playlistId,
                None,
                100,
                offset
            ) for offset in offsets
        ]

        for futures in concurrent.futures.as_completed(exec_results):
            executor_results.append(futures.result()["items"])

    if publicOnly:
        for x in executor_results:
            for y in x:
                if not y["is_local"]:
                    result["items"].append(y)
    else:
        for x in executor_results:
            for y in x:
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
        [executor.submit(
            _spotify.playlist_add_items,
            playlistId,
            tracks_to_add[(j*100):((j+1)*100)]
        ) for j in get_TaskCount(len(tracks_to_add))
        ]
    import os


def get_TaskCount(x, start_at_1=False):
    # Spotify's API wont allow more than 100 songs per POST:
    # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/#body-parameters:~:text=A%20maximum%20of%20100

    return range(1, int(math.ceil(x / 100.0))) if start_at_1 else range(0, int(math.ceil(x / 100.0)))


def dedpuplicate_existingPlaylist(_spotify: spotipy.Spotify, playlistId: str):
    playlist = getAsync(_spotify, playlistId)
    # find_all_dups()
    duplicateIDs, seenIDs, seenNameAndArtist = [], [], {}
    for track in playlist:
        duplicate = False
        seenNameAndArtistKey = f'{track["name"]}:{track["artists"][0]["name"]}'.lower(
        )
        duration = track["duration"]

        if track['id'] in seenIDs:
            duplicate = True
        else:
            if seenNameAndArtistKey in seenNameAndArtist:
                if seenNameAndArtist[seenNameAndArtistKey] - duration < 2000:
                    duplicate = True

        if duplicate:
            duplicateIDs.append(track["id"])
        seenIDs.append(track["id"])
        seenNameAndArtist == {**seenNameAndArtist,
                              seenNameAndArtistKey: duration}

    # https://github.com/JMPerez/spotify-dedup/
    remove_tracks(duplicateIDs)
    return 0


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


def remove_tracks(_spotify: spotipy.Spotify, playlistId: str, trackIDs: list):
    # TODO
    _spotify.playlist_remove_specific_occurrences_of_items(playlistId)
    return 0


def edited_this_week(_spotify: spotipy.Spotify, playlist_id: str):
    import datetime
    try:
        lastEditStr = _spotify.playlist_tracks(
            playlist_id,
            limit=1
        )["items"][0]["added_at"]
        l = datetime.datetime.strptime(lastEditStr, '%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        print("LoFi playlist was empty...")
        return False

    d = datetime.datetime.now()

    datetime_current = int(f"{d.year}{d.isocalendar()[1]}")
    datetime_lastEdit = int(f"{l.year}{l.isocalendar()[1]}")

    print(
        f"Current Week: {datetime_current}\nLast edit:    {datetime_lastEdit}")
    if datetime_current > datetime_lastEdit:
        return False
    return True


def deduplicate_backup():
    return 0
