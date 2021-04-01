import sys

from util import gist

gist_name = "disabled.json"

track = input('Enter Track URI: ') if len(sys.argv) != 2 else sys.argv[1]


if len(track) == 22:
    track = f'spotify:track:{track}'
elif len(track) != 36 or track[0:14] != 'spotify:track:':
    raise TypeError('URI format incorrect')

disabled_tracks = gist.load(gist_name)
if type(disabled_tracks) is not list:
    raise TypeError("not a list", disabled_tracks)
if track in disabled_tracks:
    print(f"Not adding {track} - already disabled")
    sys.exit(-1)
disabled_tracks.append(track)


gist.update(gist_name, disabled_tracks, f"Added track: {track}")

print(f"Added track: {track}")
