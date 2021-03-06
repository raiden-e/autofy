import argparse
import base64
import collections
import os
import sys
from time import strftime

import requests
from PIL import Image, ImageDraw, ImageFont

import config
from util import gist, playlist
from util.spotify import getsp_client

if len(sys.argv) > 3:
    raise TypeError(
        "Please specify a playlist, Image.py takes up to two arguments")


parser = argparse.ArgumentParser()
parser.add_argument(
    "plid",
    nargs='?',
    help='The id of the playlist you want to backup',
    type=str)
parser.add_argument(
    "--noplaylist",
    help='switch to only get picture',
    action="store_true")
args = parser.parse_args()

gist_name = "backup.json"

sp = getsp_client()


def watermark_photo(input_image, output_image):
    base_image = Image.open(input_image).convert('RGBA')

    width, height = base_image.size

    txt = Image.new('RGBA', base_image.size, (255, 255, 255, 0))
    fnt = ImageFont.truetype(font=os.path.join(os.path.dirname(
        __file__), 'util', 'calibri.ttf'), size=int(round(width/9)))
    drawingContext = ImageDraw.Draw(txt)

    x, y = round(width / 1.6), round(height / 1.14)

    drawingContext.text((x, y), ".Backup", font=fnt, fill=(255, 255, 255, 220))

    Image.alpha_composite(base_image, txt).convert('L').save(output_image)


def set_newPlaylist(inputPlaylist):
    try:
        playlists = gist.load(gist_name)
    except Exception:
        raise "Could not receive playlist's. Are you offline?"

    for pl in playlists['playlist']:
        if inputPlaylist['uri'] in playlists['playlist'][pl]['get'] \
                or inputPlaylist['uri'] == playlists['playlist'][pl]['get']:
            print('Playlist already backed')
            return False

    if inputPlaylist["name"] == "Discover Weekly":
        playlist_Name = f"{inputPlaylist['name']}.backup [{inputPlaylist['id']}]"
    else:
        playlist_Name = f"{inputPlaylist['name']}.backup"

    try:
        tracks = [x["track"]["uri"]
                  for x in playlist.getAsync(sp, args.plid, True)['items']]
    except Exception:
        raise "Could not get Tracks from the playlist, aborting"

    newPlaylist = sp.user_playlist_create(
        config.SPOTIPYUN,
        playlist_Name,
        public=True,
        description=f"Backup since {strftime('%d')} {strftime('%b')} {strftime('%Y')}"
    )

    with open("BackupImage.jpg", "rb") as pic:
        sp.playlist_upload_cover_image(
            newPlaylist["id"], base64.b64encode(pic.read()))

    for j in playlist.get_TaskCount(len(tracks)):
        sp.user_playlist_add_tracks(
            sp.auth_manager.username, playlist_id=newPlaylist["id"], tracks=tracks[(j*100):((j+1)*100)])

    playlists["playlist"][playlist_Name] = {
        "get": [inputPlaylist["uri"]], "set": newPlaylist["uri"]}

    playlists["playlist"] = collections.OrderedDict(
        sorted(playlists['playlist'].items()))

    comment = f"Add playlist: {playlist_Name} - ({inputPlaylist['uri']})"
    gist.update(gist_name, playlists, comment)

    print(newPlaylist["id"])
    return newPlaylist["id"]


def main():
    with open('BackupImage.jpg', 'wb') as p:
        with requests.get(sp.playlist_cover_image(args.plid)[0]["url"], allow_redirects=True) as r:
            p.write(r.content)
    watermark_photo('BackupImage.jpg', output_image='BackupImage.jpg')
    if not args.noplaylist:
        print("getting backed playlists...")
        print("setting new playlist")
        set_newPlaylist(sp.playlist(args.plid))


if __name__ == '__main__':
    main()
