import concurrent
from pprint import pprint

from util import gist, playlist
from util.sendfail import sendfail
from util.spotify import get_spotify_client

_spotify = get_spotify_client()


def backup_playlist(pl: dict):
    if type(pl["get"]) is list:
        print("GET containes is a backup of multiple playlists:")
        pprint(pl, width=120)
        Get = []
        for x in pl["get"]:
            print(f"loading:  {str(x)}")
            for item in playlist.getAsync(_spotify, x, True)["items"]:
                Get.append(item)
    else:
        print(f"loading {pl}")
        Get = playlist.getAsync(
            _spotify=_spotify,
            playlistId=pl["get"],
            publicOnly=True
        )["items"]
    Set = playlist.getAsync(
        _spotify=_spotify,
        playlistId=pl["set"],
        publicOnly=True
    )["items"]
    GetTracks, SetTracks, ToAdd = [], [], []

    for track in Get:
        try:
            GetTracks.append(track["track"]["id"])
        except TypeError as e:
            try:
                print(f"Electronic rising doing its thing?\n{e}")
                sendfail(f"Electronic rising doing its thing?\n{e}")
            except Exception as e0:
                print(f'Couldnt send fail message\n{e0}')

    try:
        [SetTracks.append(track["track"]["id"]) for track in Set]
    except Exception:
        return

    [ToAdd.append(track)
     if not track in SetTracks else None for track in GetTracks]

    if ToAdd:
        try:
            playlist.addAsync(_spotify, ToAdd, pl['set'])
            print("Added:")
            pprint(ToAdd)
        except Exception:
            sendfail(f"{pl} {pl['set']}")
    else:
        print(f"{pl['set']}  is already up to date")


def main():
    playlists = gist.load("backup.json")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for playlist in playlists["playlist"]:
            executor.submit(backup_playlist(playlists["playlist"][playlist]))
    print("Done")


if __name__ == '__main__':
    main()
