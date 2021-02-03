import concurrent
from pprint import pprint

from util import gist, playlist
from util.spotify import get_spotify_client


def filter(playlist):
    tracks = []
    for track in playlist:
        try:
            if track['track']['id']:
                tracks.append(track["track"])
        except TypeError as e:
            print(f"Electronic rising doing its thing?\n{e}")
            exceptions.append([e, track])
        except Exception as e:
            print(f"An error has occured in {track}\n{e}")
            exceptions.append([e, track])
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

    def track_to_seen(tts):
        return {
            "name": tts['name'],
            "artist": tts['artists'][0]['name'],
            "duration": tts['duration_ms'],
            "id": tts['id']
        }

    seen_tracks = [track_to_seen(tr) for tr in Set]

    def filter2(track):
        for x in seen_tracks:
            if x['id'] == track['id']:
                seen_tracks.append(track_to_seen(track))
                return False
            if x['id'] in disabled:
                return False
            if x['name'] == track['name']:
                if x['artist'] == track['artists'][0]['name']:
                    if x['duration'] - 100 <= track['duration_ms'] <= x['duration'] + 100:
                        seen_tracks.append(track_to_seen(track))
                        caught.append(x)
                        return False
        seen_tracks.append(track_to_seen(track))
        return True

    ToAdd = []
    for track in Get:
        if filter2(track):
            ToAdd.append(track['id'])

    if ToAdd:
        try:
            playlist.addAsync(_spotify, ToAdd, pl['set'])
            pprint(f"Added: {len(ToAdd)}{ToAdd}")
        except Exception as e:
            print(e)
    else:
        print(f"{pl['set']} is already up to date", end=None)

    print(f"Caught: {len(caught)}")


def main():
    print("Loading backup.json")
    playlists = gist.load("backup.json")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for playlist in playlists["playlist"]:
            executor.submit(backup_playlist(playlists["playlist"][playlist]))

    print("Exceptions:")
    pprint(exceptions)
    print("Done")


if __name__ == '__main__':
    _spotify = get_spotify_client()
    exceptions = []
    print("Loading disabled.json")
    disabled = gist.load("disabled.json")
    main()
