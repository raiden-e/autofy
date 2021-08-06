import asyncio
from pprint import pformat, pprint

from util import dc, gist, playlist
from util.spotify import get_spotify_client


def print_exceptions(exceptions):
    err_msg = f"Exceptions ({len(exceptions)}):\n" + pformat(exceptions)
    print(err_msg)
    if len(exceptions) > 0:
        try:
            asyncio.get_event_loop().run_until_complete(dc.error_log(err_msg))
        except Exception as e:
            print("DC broken?", e)


def backup_playlist(pl: dict):
    pprint(pl, width=120)

    Get = [playlist.getAsync(_spotify, x, publicOnly=True)["items"] for x in pl["get"]][0]
    Set = playlist.getAsync(_spotify, pl["set"], publicOnly=True)["items"]

    try:
        Get = [track for track in Get if track['track']]
        Set = [track for track in Set if track['track']]
    except Exception as e:
        print(e)
        exceptions.append(e)

    ToAdd = playlist.deduplify_list(main_list=Get, base_list=Set, disabled=disabled)

    if len(ToAdd) > 0:
        try:
            playlist.addAsync(_spotify, ToAdd, pl['set'])
            print(f"Added: {len(ToAdd)}")
            pprint(ToAdd, depth=2)
        except Exception as e:
            print(e)
            exceptions.append(e)
    else:
        print(f"Already up to date: {pl['set']}", end=None)


def main():
    print("Loading backup.json")
    playlists = gist.load("backup.json")

    for playlist in playlists["playlist"]:
        backup_playlist(playlists["playlist"][playlist])

    print_exceptions(exceptions)
    print("Done")


if __name__ == '__main__':
    _spotify = get_spotify_client()
    exceptions = []
    print("Loading disabled.json")
    disabled = gist.load("disabled.json")
    main()
