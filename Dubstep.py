#!/usr/env/python3
import random
import sys

try:
    import config
except ImportError:
    raise ImportError("Please make sure you rename config_template.py to config.py")
from util import gist, playlist
from util.spotify import get_spotify_client

username = config.SPOTIPYUN
dubstep_id = "6XnpwiV7hkEUMh4UsMapm2"
_spotify = get_spotify_client()
gist_name = "dubstep.json"


def get_newest_by_artist(artist):
    try:
        # This is bad but i cant get the popularity items otherwise
        artist_albums = _spotify.artist_albums(
            artist_id=artist, album_type='single,album,compilation')['items']
    except Exception as e:
        raise Exception(f"Could not get latest album for {artist}, {e}")

    def sorter(input):
        return input['release_date']
    artist_albums.sort(key=sorter, reverse=True)
    latest_release = artist_albums[0]

    if not latest_release["album_type"] == "album":
        tracks = _spotify.album_tracks(latest_release['uri'])
        tmp = [track for track in tracks['items']]
        return tmp

    tracks = _spotify.tracks([x['id'] for x in _spotify.album_tracks(
        latest_release['uri'])['items']])['tracks']

    sample_amount = random.randint(
        min(2, len(tracks)),
        min(5, len(tracks))
    )

    def sorter(input):
        return input['popularity']
    tracks.sort(key=sorter, reverse=True)

    return [tracks[first] for first in range(sample_amount)]


def main():
    print("To add an artist to the radar, run script with artist uri as argument")
    if playlist.edited_this_week(_spotify, dubstep_id):
        print("Exiting")
        return

    print("clearing playlist")
    playlist.clear(_spotify, dubstep_id)

    gist_list = gist.load(gist_name)

    ids = [x['id'] for art in gist_list for x in get_newest_by_artist(art)]

    # randomize and no doubles
    ids = list(set(ids))
    random.shuffle(ids)

    print("adding songs to playlist")
    playlist.add(
        _spotify=_spotify,
        tracks_to_add=ids,
        playlistId=dubstep_id
    )


def new_artist(artist: str):
    artist = artist.strip()
    if artist[0:8] == "spotify:" and artist[8:14] != "artist":
        print("Please make sure to pass an artist")
        return False
    try:
        artist = _spotify.artist(artist_id=artist)
    except Exception as e:
        raise AttributeError(f"Please make sure artist {artist} exists\n", e)

    x = gist.load(gist_name)
    if artist in x:
        print("Artist already in radar")
        return False
    x.append(artist['id']).sort()
    gist.update(gist_name, x, f"Add artist: {artist['id']} ({artist['name']})")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        new_artist(sys.argv[1])
    else:
        raise AttributeError("Dubstep.py takes up to 1 arg")
