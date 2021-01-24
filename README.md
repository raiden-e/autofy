# Autofy

Scripts that automatically backup Spotifyplaylist, update them and more.

![Tests](https://github.com/raiden-e/autofy/workflows/Tests/badge.svg) ![Daily Run](https://github.com/raiden-e/autofy/workflows/Daily%20Run/badge.svg)

## Licensing 🔑

[telethon](https://github.com/LonamiWebs/Telethon/blob/master/LICENSE) |
[spotipy](https://github.com/plamere/spotipy/blob/master/LICENSE.md) |
[discord.py](https://github.com/Rapptz/discord.py/blob/master/LICENSE) |
[pyGithub](https://github.com/PyGithub/PyGithub/blob/master/COPYING) |
[pytz](https://github.com/stub42/pytz/blob/master/LICENSE.txt) |
[Pillow](https://github.com/python-pillow/Pillow/blob/master/LICENSE)

## Links 📎

- [LoFi Playlist](https://open.spotify.com/playlist/5h9LqGUUE4FKQfVwgAu1OA)
- [Dubstep Radar](https://open.spotify.com/playlist/6XnpwiV7hkEUMh4UsMapm2)
- [Daily Song](http://t.me/Daily_Track)
- [Track des Tages](http://t.me/TrackDesTages)
- [Discord Daily Song](https://discord.gg/wDaVDtx)

## Lofi ☕

A script to pick around 150 Lo-Fi songs and drop them into a chilled weekly automated [playlist](https://open.spotify.com/playlist/5h9LqGUUE4FKQfVwgAu1OA).
Lo-Fi Hip-Hop is some of the chilliest beats you will ever hear, and it helps me study, code, play games and relax.

## Backup 📚

Spotify has some good playlists. However they get updated sometimes and some songs get removed from them. This script goes through a number of playlists and archives their tracks. Check out the [Night Rider Playlist](https://open.spotify.com/playlist/5p0qHPgujEMFGSRms689v8) for example.

### Requirements for Backup

You need to go to [gist.github.com](https://gist.github.com/) and create a gist with a file called `backup.json`

### Image

Automatically adds a playlist to the gist which contians Backup.py 's list of uri's.

## DailySong 🎶

Send's a random song from a Spotify playlist to
[Track des Tages](t.me/TrackDesTages),
[Daily Track](t.me/Daily_Track)
and to my
[Discord](https://discord.gg/wDaVDtx)
at 12 PM CEST

## Dubstep 🚑

So I like this genre but Spotifys algorithms are kinds poor when it comes to recommandations and also the personal radar changes wheneven you listen to something new. _espacially_ when you listen to a single song from a popular artist. So I summed up some decent artists in a gist and this script pulls the latest releases from them and loads them into a [playlist](https://open.spotify.com/playlist/6XnpwiV7hkEUMh4UsMapm2) on a weekly basis. Also if the latest release was an album, it pick the 2-5 most popular tracks from it.

## Now Playing ▶

Show the currently playing song on Spotify and get the artist, song name, album name and cover.

## Examples

```powershell
python LoFi.py

python Image.py spotify:playlist:5h9LqGUUE4FKQfVwgAu1OA

python DailySong.py

python Dubstep.py

python Backup.py
```

## Setup

### Requirements

- `python`
  - `spotipy`
  - `telethon`
  - `discord.py`
  - `pyGithub`
  - `pytz`
  - `Pillow`

Create a [Telegram application](https://my.telegram.org/)

Create a [Spotify application](https://developer.spotify.com/dashboard/)

Create a [Discord bot](https://discord.com/developers)

Get your [gist token](https://github.com/settings/tokens/new)

Rename `config_template.py` to `config.py`.
Save your api hashes and id's to `config.py`

Install [Python](https://www.python.org/downloads/)

Open Powershell/CMD and run the following commands:

```powershell
python -m venv venv

.\venv\Scrupts\activate.ps1

pip install -r requirements.txt
```

Now you can run a script manually like so:

```powershell
python Image.py spotify:playlist:xxxxxxxxxx # with `xx...x` being your playlist id
```