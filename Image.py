import argparse
import collections
import os
import sys

import requests
from PIL import Image, ImageDraw, ImageFont

from util import gist, playlist
from util.spotify import get_spotify_client

if len(sys.argv) > 3:
    raise TypeError(
        "Please specify a playlist, Image.py takes up to two arguments")


parser = argparse.ArgumentParser()
parser.add_argument("plid", nargs='?', help='The id of the playlist you want to backup', type=str)
parser.add_argument("--noplaylist", help='switch to only get picture', action="store_true")
parser.add_argument('-f', '--file')
args = parser.parse_args()

gist_name = "autofy.json"

sp = get_spotify_client()


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
        raise FileNotFoundError("Could not receive playlist's. Are you offline?")

    backup = playlists['backup']

    for pl in backup:
        if inputPlaylist['uri'] in backup[pl]['get'] or inputPlaylist['uri'] == backup[pl]['get']:
            print('Playlist already backed')
            return False

    playlist_Name = f"{inputPlaylist['name']}.backup"
    if inputPlaylist["name"] == "Discover Weekly":
        playlist_Name += f" [{inputPlaylist['id']}]"

    tracks = [x["track"]["uri"] for x in playlist.getAsync(sp, inputPlaylist['id'], True)['items']]

    newPlaylist = playlist.new_playlist(sp, tracks, playlist_Name, img)

    backup[playlist_Name] = {"get": [inputPlaylist["uri"]], "set": newPlaylist["uri"]}

    backup = collections.OrderedDict(sorted(backup.items()))

    comment = f"Add playlist: {playlist_Name} - ({inputPlaylist['uri']})"
    gist.update(gist_name, playlists, comment)

    print(newPlaylist["id"])
    return newPlaylist["id"]


def image_playlist(plid):
    with open(img, 'wb') as p:
        with requests.get(sp.playlist_cover_image(plid)[0]["url"], allow_redirects=True) as r:
            p.write(r.content)
    watermark_photo(img, output_image=img)

    if args.noplaylist:
        return

    print("getting backed playlists...")
    print("setting new playlist")
    set_newPlaylist(sp.playlist(plid))


def main():
    if args.plid and args.file:
        print("Please only specify a file OR a playlist")
        return

    if args.file:
        with open(args.file, 'r', encoding='utf-8-sig') as f:
            plids = f.readlines()
        for plid in plids:
            bruh = plid.strip()
            print(f"Loading: {bruh}")
            if playlist.verify_url(bruh):
                image_playlist(bruh)
            else:
                print(f"Invalid URL: {bruh}")
    else:
        image_playlist(args.plid)


if __name__ == '__main__':
    img = 'BackupImage.jpg'
    main()
