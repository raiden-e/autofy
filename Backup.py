import sys
from pprint import pformat, pprint

from spotipy.exceptions import SpotifyOauthError

from util import gist, playlist, runlog
from util.spotify import get_spotify_client


def print_exceptions(exepts):
    print(f"Exceptions ({len(exepts)}):\n" + pformat(exepts))


def backup_playlist(pl: dict):
    # Merge all source playlists into one list
    Get = []
    for playlist_id in pl["get"]:
        try:
            items = playlist.getAsync(_spotify, playlist_id, publicOnly=True)["items"]
            Get.extend(items)
            runlog.source(playlist_id, ok=True, tracks=len(items))
        except Exception as e:
            print(f"  Error fetching playlist {playlist_id}: {e}")
            exceptions.append(e)
            runlog.source(playlist_id, ok=False, error=e)

    if not Get:
        print("  No tracks found in source playlists")
        runlog.update(status="no_tracks")
        return

    Set = playlist.getAsync(_spotify, pl["set"], publicOnly=True)["items"]
    print(f"  Exporting: {pl['set']}")

    try:
        Get = [track for track in Get if track["track"]]
        Set = [track for track in Set if track["track"]]
    except Exception as e:
        print(e)
        exceptions.append(e)
        runlog.error(e, "filter")

    Tracks = playlist.deduplify_list(main_list=Get, base_list=Set, ignore=ignore)
    runlog.update(fetched=len(Get), existing=len(Set))

    if len(Tracks) > 0:
        ToAdd = [z["track"]["uri"] for z in Tracks]
        try:
            playlist.addAsync(_spotify, ToAdd, pl["set"])
            print(f"Added: {len(ToAdd)}")
            runlog.update(status="added", added=len(ToAdd))
            pprint(ToAdd, depth=2)
            msg = "get:\n  " + "\n  ".join([x for x in pl["get"]])
            msg += "\nset\n  " + pl["set"]
            print(f"Backed:\n{msg}")
        except Exception as e:
            print(e)
            exceptions.append(e)
            runlog.update(status="error")
            runlog.error(e, "add")
    else:
        print(f"Already up to date: {pl['set']}", end="\n")
        runlog.update(status="uptodate")


def main():
    print("loading...")
    for pl in data["backup"]:
        runlog.target(pl, set_id=str(data["backup"][pl]["set"]).strip())
        get_list = data["backup"][pl]["get"]
        for gid in list(get_list):
            if not playlist.verify_url(gid):
                print(f"\033[93mPlaylist {gid} aint legit. imma remove it\033[0m")
                runlog.source(gid, ok=False, error="invalid or unsupported playlist id (skipped)")
                get_list.remove(gid)

        if len(get_list) == 0:
            print(
                f"\033[91mAyo there aint no valid 'get' playlists for {pl}, wth man get rid of this shit!...\033[0m"
            )
            continue

        if data["backup"][pl]["set"].strip() == "":
            print(f"Empty set: {pl}")
            runlog.update(status="skipped")
            continue
        msg = pl + "\nget:\n  " + "\n  ".join([x for x in data["backup"][pl]["get"]])
        msg += "\nset:\n  " + data["backup"][pl]["set"]
        print(f"Backing up: {msg}")
        backup_playlist(data["backup"][pl])
    runlog.end_target()

    runlog.extra(exceptions=len(exceptions))
    print_exceptions(exceptions)
    print("Done")


if __name__ == "__main__":
    # runlog.Run appends one JSON line per run to runs/runs.jsonl (dashboard data);
    # it never swallows exceptions and never fails the backup itself.
    with runlog.Run("Backup"):
        try:
            _spotify = get_spotify_client()
            print("Loading autofy.json...")
            data = gist.load("autofy.json")
            print("Loading autofy.json completed.")
            print("Loading Loading ignore list...")
            ignore = playlist.getAsync(_spotify, data["ignore"])["items"]
            print("Loading ignore list completed.")
        except SpotifyOauthError as e:
            # Fatal, and actionable: the cached token is dead (revoked/expired) and can't
            # be refreshed. No point running — bail with one clear line + non-zero exit so
            # the scheduler logs a short message instead of a 40-line traceback.
            runlog.run_error(e, "auth")
            print(
                f"\033[91mAUTH FAILED: {e}\033[0m\n"
                "Re-authorize: sudo docker compose -f "
                "/mnt/base/config/nas/deploy/autofy.yml run --rm -it autofy python Backup.py"
            )
            sys.exit(1)

        exceptions = []
        main()
