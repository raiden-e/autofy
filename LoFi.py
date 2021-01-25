#!/usr/env/python3
import random

from util import playlist
from util.spotify import get_spotify_client

username = "raiden_e"
lofi_id = "5h9LqGUUE4FKQfVwgAu1OA"
_spotify = get_spotify_client()


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
    lofi_list = playlist.deduplify_list(lofi_list, lofi_base)

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
