#!/usr/env/python3
import random

from util import playlist
from util.spotify import get_spotify_client

username = "raiden_e"
lofi_id = "5h9LqGUUE4FKQfVwgAu1OA"
_spotify = get_spotify_client()


def deduplify_list(potential_duplicates: list, reference_deuplicates: list):
    def print_diff(a, b):
        print("Duplicate Meta:\n {:>21}|{:<0}".format(
            a['track']['name'], b['track']['name']))
        print("{:>32}|{:<0}".format(
            a['track']['id'], b['track']['id']))
        print("{:>32}|{:<0}".format(
            a['track']['artists'][0]['name'], b['track']['artists'][0]['name']))

    for x in reference_deuplicates:
        for y in potential_duplicates:
            if x["track"]["id"] == y["track"]["id"]:
                print("Duplicate ID: {0:30}- {1}".format(
                    y['track']['name'], f"{x['track']['id']}|{y['track']['id']}"))
                potential_duplicates.remove(y)
                continue
            # if duration somewhat same, artist and track name same
            if y["track"]["duration_ms"] - 100 <= x["track"]["duration_ms"] <= y["track"]["duration_ms"] + 100:
                if x["track"]["name"] == y["track"]["name"]:
                    if len(x["track"]["artists"]) == 1:
                        if x["track"]["artists"][0] in y["track"]["artists"]:
                            print_diff(x, y)
                            potential_duplicates.remove(y)
                            continue
                    else:
                        for artist in x["track"]["artists"]:
                            if artist['name'] in y["track"]["artists"]:
                                print_diff(x, y)
                                potential_duplicates.remove(y)
                                continue

    return potential_duplicates


def randomize_lofi(initial_track: dict, lofi_base: list, lofi_list: list):
    try:
        list_size = 250 - 1  # We count -1 bc of initial track
        list_sample = random.sample(lofi_list, (list_size - len(lofi_base)))
        final_sample = random.sample([*lofi_base, *list_sample], list_size)
        return [z["track"]["id"] for z in [initial_track, *final_sample]]
    except Exception:
        raise "Could not sample lofibase or lofilist"


def main():
    if playlist.edited_this_week(_spotify, lofi_id):
        print("Exiting, Ran this week")
        return

    print("getting playlist Backup")
    lofi_list = playlist.getAsync(
        _spotify, "31k9ZXIfUi9v5mpbfg6FQH", True)["items"]
    print("getting playlist base")
    lofi_base = playlist.get(
        _spotify, "5adSO5spsp0tb48t2MyoD6", True)['items']

    print("deduplifying list")
    lofi_list = deduplify_list(lofi_list, lofi_base)

    initial_track = random.choice(lofi_base)
    lofi_base.remove(initial_track)
    print(f"chose the initial track: {initial_track['track']['name']}")

    print("randomizing")
    weekly_playlistIds = randomize_lofi(initial_track, lofi_base, lofi_list)

    print("clearing playlist")
    playlist.clear(_spotify, lofi_id)

    print("adding songs to playlist")
    playlist.add(
        _spotify=_spotify,
        tracks_to_add=weekly_playlistIds,
        playlistId=lofi_id
    )


if __name__ == '__main__':
    main()
