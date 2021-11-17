#!/usr/env/python3
import random

from util import gist, playlist
from util.spotify import get_spotify_client

lofi = {
    "name": "lofi",
    "id": "5h9LqGUUE4FKQfVwgAu1OA",
    "backup": "31k9ZXIfUi9v5mpbfg6FQH",
    "base": "5adSO5spsp0tb48t2MyoD6",
}
japan = {
    "name": "japan",
    "id": "6Cu6fL6djm63Em0i93IRUW",
    "backup": "19yEs2hB6J5FwHrGMsIlZQ",
    "base": "7EdczIpYSY7aUBSMqgGguV",
}


def main(plid: str, backup: str, base: str):
    def randomize_tracks(lofi_base: list, lofi_list: list):
        try:
            list_size = 250 - 1  # We count -1 bc of initial track
            list_sample = random.sample(lofi_list, (list_size - len(lofi_base)))
            final_sample = random.sample(lofi_base + list_sample, list_size)
            return [x['track']['uri'] for x in [initial_track, *final_sample]]
        except Exception:
            raise Exception("Could not sample lofibase or lofilist")

    print("getting playlist Backup")
    lofi_list = playlist.getAsync(_spotify, backup, True)["items"]
    print("getting playlist base")
    lofi_base = playlist.get(_spotify, base, True)['items']

    print("deduplifying list")
    lofi_list = playlist.deduplify_list(lofi_list, lofi_base, ignore)

    initial_track = random.choice(lofi_base)
    lofi_base.remove(initial_track)
    print(f"chose the initial track: {initial_track['track']['name']}")

    print("randomizing")
    weekly_playlistIds = randomize_tracks(lofi_base, lofi_list)
    print(weekly_playlistIds)

    print("clearing playlist")
    playlist.clear(_spotify, plid)

    print("adding songs to playlist")
    playlist.add(
        _spotify=_spotify,
        tracks_to_add=weekly_playlistIds,
        playlistId=plid
    )


if __name__ == '__main__':
    _spotify = get_spotify_client()
    print("loading gist")
    data = gist.load("autofy.json")
    print("loading ignored tracks...")
    ignore = playlist.getAsync(_spotify, data['ignore'])["items"]

    for x in (lofi, japan):
        if playlist.edited_this_week(_spotify, lofi['id']):
            print(f"Ran this week: {x['name']}")
            continue
        print(f'shuffeling {x["name"]}')
        main(x['id'], x['backup'], x['base'])
