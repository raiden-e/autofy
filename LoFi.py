#!/usr/env/python3
import random
import sys

from spotipy.exceptions import SpotifyOauthError

from util import gist, playlist, runlog
from util.spotify import get_spotify_client

lofi = {
    "name": "lofi",
    "id": "6BjUHlMg8Qkb6VktjzBdac",
    "backup": "0wd5N98lZyiNpOm4nQJqc5",
    "base": "0itii8CWNFCSyyae6Nyh82",
}
japan = {
    "name": "japan",
    "id": "0DBoAeAcD19yxfm3VkG3K9",
    "backup": "0M9SjFcNecW4XlDUSHTIRA",
    "base": "2qs5yzdS5o2imiHbbxZM01",
}


def main(plid: str, backup: str, base: str):
    def randomize_tracks(lofi_base: list, lofi_list: list):
        list_size = 250 - 1  # We count -1 bc of initial track
        needed = list_size - len(lofi_base)
        if needed > len(lofi_list):
            raise ValueError(
                f"Not enough tracks: need {needed} from backup but only "
                f"{len(lofi_list)} available (base has {len(lofi_base)})"
            )

        list_sample = random.sample(lofi_list, needed)
        final_sample = random.sample(lofi_base + list_sample, list_size)
        return [x["track"]["uri"] for x in [initial_track, *final_sample]]

    print("getting playlist Backup")
    lofi_list = playlist.getAsync(_spotify, backup, True)["items"]
    print("getting playlist base")
    lofi_base = playlist.get(_spotify, base, True)["items"]

    print("deduplifying list")
    lofi_list = playlist.deduplify_list(lofi_list, lofi_base, ignore)

    initial_track = random.choice(lofi_base)
    lofi_base.remove(initial_track)
    print(f"chose the initial track: {initial_track['track']['name']}")

    print("randomizing")
    weekly_playlistIds = randomize_tracks(lofi_base, lofi_list)
    print(f"Generated {len(weekly_playlistIds)} tracks to add (should be 250)")

    print(f"clearing playlist {plid}")
    playlist.clear(_spotify, plid)

    print("adding songs to playlist")
    playlist.add(_spotify=_spotify, tracks_to_add=weekly_playlistIds, playlistId=plid)
    runlog.update(status="added", added=len(weekly_playlistIds))


if __name__ == "__main__":
    # runlog.Run appends one JSON line per run to runs/runs.jsonl (dashboard data)
    with runlog.Run("LoFi"):
        try:
            _spotify = get_spotify_client()
            print("loading gist")
            data = gist.load("autofy.json")
            print("loading ignored tracks...")
            ignore = playlist.getAsync(_spotify, data["ignore"])["items"]

            for x in (lofi, japan):
                print(f"Current playlist: {x['name']}")
                runlog.target(x['name'], set_id=x['id'])
                if playlist.edited_this_week(_spotify, lofi['id']):
                    print(f"Ran this week: {x['name']}")
                    runlog.update(status="skipped", reason="already ran this week")
                    continue
                print('shuffeling...')
                main(x['id'], x['backup'], x['base'])
        except SpotifyOauthError as e:
            # Cached token dead (revoked/expired) — bail with one clear line + non-zero exit
            # instead of a 40-line traceback in the scheduler log.
            runlog.run_error(e, "auth")
            print(
                f"\033[91mAUTH FAILED: {e}\033[0m\n"
                "Re-authorize: sudo docker compose -f "
                "/mnt/base/config/nas/deploy/autofy.yml run --rm -it autofy python Backup.py"
            )
            sys.exit(1)
