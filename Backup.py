from pprint import pformat, pprint

from util import gist, playlist
from util.spotify import get_spotify_client

msg = ""

def print_exceptions(exepts):
    print(f"Exceptions ({len(exepts)}):\n" + pformat(exepts))

def backup_playlist(pl: dict):
    Get = [playlist.getAsync(_spotify, x, publicOnly=True)["items"] for x in pl["get"]][0]
    Set = playlist.getAsync(_spotify, pl["set"], publicOnly=True)["items"]
    print(f"  Exporting: {pl['set']}")


    try:
        Get = [track for track in Get if track['track']]
        Set = [track for track in Set if track['track']]
    except Exception as e:
        print(e)
        exceptions.append(e)

    Tracks = playlist.deduplify_list(main_list=Get, base_list=Set, ignore=ignore)

    if len(Tracks) > 0:
        ToAdd = [z['track']['uri'] for z in Tracks]
        try:
            playlist.addAsync(_spotify, ToAdd, pl['set'])
            print(f"Added: {len(ToAdd)}")
            pprint(ToAdd, depth=2)
            msg = "get:\n  " + "\n  ".join([x for x in pl["get"]])
            msg += "\nset\n  " + pl["set"]
            print(f"Backed:\n{msg}")
        except Exception as e:
            print(e)
            exceptions.append(e)
    else:
        print(f"Already up to date: {pl['set']}", end="\n")


def main():
    for pl in data["backup"]:
        if data["backup"][pl]['set'].strip() == "":
            print(f"Empty set: {pl}")
            continue
        msg = pl + "\nget:\n  " + "\n  ".join([x for x in data["backup"][pl]["get"]])
        msg += "\nset:\n  " + data["backup"][pl]["set"]
        print(f"Backing up: {msg}")
        backup_playlist(data["backup"][pl])

    print_exceptions(exceptions)
    print("Done")


if __name__ == '__main__':
    _spotify = get_spotify_client()
    print("Loading autofy.json")
    data = gist.load("autofy.json")
    ignore = playlist.getAsync(_spotify, data['ignore'])['items']
    exceptions = []
    main()
