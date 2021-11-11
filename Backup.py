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


def backup_playlist(pl: dict, disabled):
    Get = [playlist.getAsync(_spotify, x, publicOnly=True)["items"] for x in pl["get"]][0]
    Set = playlist.getAsync(_spotify, pl["set"], publicOnly=True)["items"]
    print(f"  Exporting: {pl['set']}")


    try:
        Get = [track for track in Get if track['track']]
        Set = [track for track in Set if track['track']]
    except Exception as e:
        print(e)
        exceptions.append(e)

    Tracks = playlist.deduplify_list(main_list=Get, base_list=Set, disabled=disabled)

    if len(Tracks) > 0:
        ToAdd = [z['track']['uri'] for z in Tracks]
        try:
            playlist.addAsync(_spotify, ToAdd, pl['set'])
            print(f"Added: {len(ToAdd)}")
            pprint(ToAdd, depth=2)
        except Exception as e:
            print(e)
            exceptions.append(e)
    else:
        print(f"Already up to date: {pl['set']}", end="\n")


def main():
    for playlist in data["backup"]:
        print(f"Backing up: {playlist}")
        backup_playlist(data["backup"][playlist], disabled)

    print_exceptions(exceptions)
    print("Done")


if __name__ == '__main__':
    _spotify = get_spotify_client()
    print("Loading autofy.json")
    data = gist.load("autofy.json")
    disabled = playlist.getAsync(_spotify, data['disabled'])['items']
    exceptions = []
    main()
