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

    with concurrent.futures.ThreadPoolExecutor() as executor:
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
                if not y["is_local"] and y['track'] is not None:
                    result["items"].append(y)
    else:
        for x in executor_results:
            for y in x:
                if y['track'] is not None:
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
            tracks_to_add[(j*100):((j+1)*100)])
            for j in get_TaskCount(len(tracks_to_add))]


def get_TaskCount(x, start_at_1=False):
    # Spotify's API wont allow more than 100 songs per POST:
    # https://developer.spotify.com/documentation/web-api/reference/playlists/add-tracks-to-playlist/#body-parameters:~:text=A%20maximum%20of%20100

    return range(1 if start_at_1 else 0, int(math.ceil(x / 100.0)))


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

    print(
        f"Current Week: {datetime_current}\nLast edit:    {datetime_lastEdit}")
    if datetime_current > datetime_lastEdit:
        print("continuing")
        return False
    return True


def deduplify_list(main_list: list, base_list: list, disabled: list):
    def print_diff(a, b):
        print("Duplicate Meta:\n{:>32}|{:<0}".format(
            a['track']['name'], b['name']))
        print("{:>32}|{:<0}".format(
            a['track']['id'], b['id']))
        print("{:>32}|{:<0}".format(
            a['track']['artists'][0]['name'], b['artists'][0]))

    def track_to_seen(track):
        return {
            "name": track['name'],
            "artists": [artist['name'] for artist in track['artists']],
            "duration": track['duration_ms'],
            "id": track['id']
        }

    seen_tracks = [track_to_seen(track['track']) for track in base_list]

    for x in main_list:
        x_tr = x['track']
        if x_tr['id'] in disabled:
            main_list.remove(x)
            continue

        def inner():
            for y in seen_tracks:
                if x_tr["id"] == y["id"]:
                    print("Duplicate ID: {0:30}- {1}".format(
                        y['name'], f"{x_tr['id']}|{y['id']}"))
                    seen_tracks.append(track_to_seen(x_tr))
                    main_list.remove(x)
                    return

                conditions = (
                    # if duration somewhat same, artist and track name same
                    abs(y["duration"] - x_tr["duration_ms"]) <= 100,
                    x_tr["name"] == y["name"],
                )
                if all(conditions):
                    for artist in x_tr["artists"]:
                        if artist['name'] in y["artists"]:
                            seen_tracks.append(track_to_seen(x_tr))
                            print_diff(x, y)
                            main_list.remove(x)
                            return
            seen_tracks.append(track_to_seen(x_tr))
        inner()

    return main_list
