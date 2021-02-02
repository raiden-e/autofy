import concurrent
from pprint import pprint

from util import gist, playlist
from util.sendfail import sendfail
from util.spotify import get_spotify_client

_spotify = get_spotify_client()

exceptions = []

# Will remove if works reliably
# if type(pl["get"]) is list:
#     print("GET containes is a backup of multiple playlists:")
#     pprint(pl, width=120)
#     Get = []
#     for x in pl["get"]:
#         print(f"loading: {str(x)}")
#         Get.extend(playlist.getAsync(_spotify, x, True)["items"])
# else:
#     print(f"loading {pl}")
#     Get = playlist.getAsync(_spotify, pl["get"], True)["items"]

def filter(playlist):
    tracks = []
    for track in playlist:
        try:
            if track['track'] is not None:
                tracks.append(track["track"])
        except TypeError as e:
            print(f"Electronic rising doing its thing?\n{e}")
            exceptions.append(track)
        except Exception as e:
            print(f"An error has occured in {track}\n{e}")
            exceptions.append(track)
    return tracks

def backup_playlist(pl: dict):
    pprint(pl, width=120)
    caught = []
    Get = []
    for x in pl["get"]:
        print(f"loading: {x}")
        Get.extend(playlist.getAsync(_spotify, x, publicOnly=True)["items"])

    Set = playlist.getAsync(_spotify, pl["set"], publicOnly=True)["items"]

    Get = filter(Get)
    Set = filter(Set)

    seen_tracks = [
        {
            "name": x['name'],
            "artist": x['artists'][0]['name'],
            "duration": x['duration_ms'],
            "id": x['id']
        }for x in Set
    ]

    def filter2(track):
        for x in seen_tracks:
            if x['id'] == track['id']:
                seen_tracks.append(track)
                return True
            if x['name'] == track['name']:
                if x['artist'] == track['artists'][0]['name']:
                    if x['duration'] -100 <= track['duration_ms'] <= x['duration'] + 100:
                        seen_tracks.append(track)
                        caught.append(x)
                        return True
        seen_tracks.append(track)
        return False

    ToAdd = []
    for track in Get:
        if filter2(track):
            ToAdd.append(track)

    if ToAdd:
        try:
            playlist.addAsync(_spotify, ToAdd, pl['set'])
            pprint(f"Added: {ToAdd['name']} by {ToAdd['artists'][0]['name']}")
            # pprint(ToAdd)
        except Exception as e:
            print(e)
    else:
        print(f"{pl['set']} is already up to date")

    print(f"Caught: {len(caught)}")


def main():
    playlists = gist.load("backup.json")
    # TODO disabled = gist.load("disabled.json")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for playlist in playlists["playlist"]:
            executor.submit(backup_playlist(playlists["playlist"][playlist]))
    print("Done")


if __name__ == '__main__':
    main()
