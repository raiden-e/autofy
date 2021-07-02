from pprint import pprint

from util import gist, playlist
from util.spotify import get_spotify_client


def filter(playlist):
    tracks = []
    for track in playlist:
        try:
            if track['track']['id']:
                tracks.append(track)
        except TypeError as e:
            print(f"Electronic rising doing its thing?\n{e}")
            exceptions.append([e, track, playlist['id']])
        except Exception as e:
            print(f"An error has occured in {track}\n{e}")
            exceptions.append([e, track, playlist['id']])
    return tracks


def backup_playlist(pl: dict):
    pprint(pl, width=120)

    Get = [playlist.getAsync(_spotify, x, publicOnly=True)["items"] for x in pl["get"]][0]
    Set = playlist.getAsync(_spotify, pl["set"], publicOnly=True)["items"]

    Get = filter(Get)
    Set = filter(Set)

    ToAdd = playlist.deduplify_list(main_list=Get, base_list=Set)

    if ToAdd:
        try:
            playlist.addAsync(_spotify, ToAdd, pl['set'])
            pprint(f"Added: {len(ToAdd)}{ToAdd}")
        except Exception as e:
            print(e)
    else:
        print(f"Already up to date: {pl['set']}", end=None)


def main():
    print("Loading backup.json")
    playlists = gist.load("backup.json")

    for playlist in playlists["playlist"]:
        backup_playlist(playlists["playlist"][playlist])

    print("Exceptions:")
    pprint(exceptions)
    print("Done")


if __name__ == '__main__':
    _spotify = get_spotify_client()
    exceptions = []
    print("Loading disabled.json")
    disabled = gist.load("disabled.json")
    main()
