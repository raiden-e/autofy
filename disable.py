import sys

from util import gist

gist_name = "disabled.json"

if len(sys.argv) != 2:
    raise TypeError("Please provide one track")

track = sys.argv[1]

if len(track) != 22:
    if len(track) != 36 or track[0:14] != 'spotify:track:':
        raise TypeError('URI format incorrect')
else:
    track = f'spotify:track:{track}'

disabled_tracks = gist.load(gist_name)
if type(disabled_tracks) is not list:
    raise TypeError("not a list", disabled_tracks)
if track in disabled_tracks:
    print(f"Not adding {track} - already disabled")
    exit(-1)
disabled_tracks.append(track)


# gist.update(gist_name, disabled_tracks, f"Added track: {track}")

print(f"Added track: {track}")
