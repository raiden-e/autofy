#!/usr/env/python3
import random
import sys

from util import gist, playlist
from util.spotify import get_spotify_client

dubstep_id = "6XnpwiV7hkEUMh4UsMapm2"
gist_name = "autofy.json"
_spotify = get_spotify_client()


def get_newest_by_artist(artist):
    try:
        # This is bad but i cant get the popularity items otherwise
        artist_albums = _spotify.artist_albums(
            artist_id=artist, album_type='single,album,compilation')['items']
    except Exception as e:
        print(f"Could not get latest album for {artist}")
        print(e)
        return False

    def sorter_date(x):
        return x['release_date']
    artist_albums.sort(key=sorter_date, reverse=True)
    latest_release = artist_albums[0]

    if not latest_release["album_type"] == "album":
        tracks = _spotify.album_tracks(latest_release['uri'])
        tmp = list(tracks['items'])
        return tmp

    tracks = _spotify.tracks([x['id'] for x in _spotify.album_tracks(
        latest_release['uri'])['items']])['tracks']

    sample_amount = random.randint(
        min(2, len(tracks)),
        min(5, len(tracks))
    )

    def sorter_pop(x):
        return x['popularity']
    tracks.sort(key=sorter_pop, reverse=True)

    return [tracks[first] for first in range(sample_amount)]


def main():
    print("To add an artist to the radar, run script with artist uri as argument")
    if playlist.edited_this_week(_spotify, dubstep_id):
        print("Exiting")
        return

    print("clearing playlist")
    playlist.clear(_spotify, dubstep_id)

    gist_list = gist.load(gist_name)
    dub_list = gist_list['dubstep']

    ids = [x['id'] for art in dub_list for x in get_newest_by_artist(art)]

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

    gist_list = gist.load(gist_name)
    dub_list = gist_list['dubstep']
    if artist['id'] in dub_list:
        print("Artist already in radar")
        return False
    dub_list.append(artist['id'])
    dub_list.sort()
    gist_list['dubstep'] = dub_list
    print(f"added {artist['name']}")
    gist.update(gist_name, gist_list, f"Add artist: {artist['id']} ({artist['name']})")
    return True


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        new_artist(sys.argv[1])
    else:
        raise AttributeError("Dubstep.py takes up to 1 arg")
