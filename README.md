# Autofy

<img src="https://github.com/raiden-e/autofy/workflows/Tests/badge.svg" alt="Tests"/> <img src="[https://github.com/raiden-e/autofy/workflows/Daily%20Run/badge.svg](https://github.com/raiden-e/autofy/actions/workflows/DailyRun.yml/badge.svg)" alt="Daily Run" style="padding-left: 5px" />

_Scripts that automatically backup, update Spotify playlists etc._

## Licensing 🔑

| [Pillow][1] | [pyGithub][2] | [pytz][3] | [spotipy][4] | [telethon][5] |
| ----------- | ------------- | --------- | ------------ | ------------- |

[1]: https://github.com/python-pillow/Pillow/blob/master/LICENSE
[2]: https://github.com/PyGithub/PyGithub/blob/master/COPYING
[3]: https://github.com/stub42/pytz/blob/master/LICENSE.txt
[4]: https://github.com/plamere/spotipy/blob/master/LICENSE.md
[5]: https://github.com/LonamiWebs/Telethon/blob/master/LICENSE

## Links 📎

| [Daily Song][6] | [Discord Daily Song][7] | [Dubstep Radar][8] | [LoFi Playlist][9] | [Track des Tages][10] | [Trappin in Japan][11] |
| --------------- | ----------------------- | ------------------ | ------------------ | --------------------- | ---------------------- |

[6]: http://t.me/Daily_Track
[7]: https://discord.gg/wDaVDtx
[8]: https://open.spotify.com/playlist/7lKB7kFwjFjFz2fEGZm82X
[9]: https://open.spotify.com/playlist/6BjUHlMg8Qkb6VktjzBdac
[10]: http://t.me/TrackDesTages
[11]: https://open.spotify.com/playlist/0DBoAeAcD19yxfm3VkG3K9

## Lofi ☕

A script to pick around 250 Lo-Fi songs and drop them into a chilled weekly automated [playlist][9].

Lo-Fi Hip-Hop is some of the chilliest beats you will ever hear, and it helps me study, code, play games, and relax.

## Backup 📚

Spotify has some good playlists. However, they update them sometimes, such that they remove good songs from them.
This script goes through several playlists and archives their tracks.

Check out the [Night Rider Playlist](https://open.spotify.com/playlist/37i9dQZF1DX6GJXiuZRisr) and the [Night Rider Backup](https://open.spotify.com/playlist/01aaWE3KEYkUEG6cPNc9Dg).

### Requirements for Backup

You need to go to [gist.github.com](https://gist.github.com) and create a gist with a file called `autofy.json`. In this gist, create a file called `autofy.json` and paste the following basic structure

```json
{
  "backup": {
  }
}
```

Adding single playlist automatically with Image.py: [Image](#image)



Adding a playlist manually:

```json
{
  "backup": {
    "My Playlist No. 1": {
      "get": [
        "spotify:playlist:RanDoMstuff12312312312"
      ],
      "set": "spotify:playlist:uriToMyPlaylistNo1backup"
    }
  }
}
```

you can also have multiple plyalist be merged into one backup list, like my [lofi backup](https://open.spotify.com/playlist/0wd5N98lZyiNpOm4nQJqc5):

```json
{
  "backup": {
    "zzLofi": {
      "get": [
        "spotify:playlist:0vvXsWCC9xrXsKd4FyS8kM",
        "spotify:playlist:74sUjcvpGfdOvCHvgzNEDO",
        "spotify:playlist:37i9dQZF1DXc8kgYqQLMfH",
        "spotify:playlist:37i9dQZF1DX8Uebhn9wzrS",
        "spotify:playlist:37i9dQZF1DX9RwfGbeGQwP",
        "spotify:playlist:37i9dQZF1DWZZbwlv3Vmtr",
        "spotify:playlist:37i9dQZF1DX0SM0LYsmbMT"
      ],
      "set": "spotify:playlist:0wd5N98lZyiNpOm4nQJqc5"
    }
  }
}
```

### Image

Automatically adds a playlist to the gist containing Backup.py 's list of URI's.

```powershell
.\venv\Scripts\activate.ps1
python .\Image.py --plid <link to playlist> --file <path to >
```
parser.add_argument("plid", nargs='?', help='The id of the playlist you want to backup', type=str)
parser.add_argument("--noplaylist", help='switch to only get picture', action="store_true")
parser.add_argument('-f', '--file')
## DailySong 🎶

Send's a random song from a Spotify playlist to
[Track des Tages](t.me/TrackDesTages),
[Daily Track](t.me/Daily_Track),
and my
[Discord](https://discord.gg/wDaVDtx)
at noon CEST.

## Dubstep 🚑

So I like this genre, but Spotify's algorithms are kind of poor when it comes to recommendations.
The personal radar changes whenever you listen to something new. _Especially_ when you recently listened to songs by popular artists.
So I summed up some decent dubstep artists in a [gist](https://gist.github.com).
This script pulls the latest releases from those artists and loads them into a [playlist](https://open.spotify.com/playlist/6XnpwiV7hkEUMh4UsMapm2) every week.
If the latest release was an album, it picks the 2-5 most popular tracks.

## Now Playing ▶

Show the currently playing song on Spotify and get the artist, song name, album name, and cover.
This script continuously  saves the name of the song, artist, and album in a text file in the user's home folder.

```powershell
.\venv\Scripts\activate.ps1
python .\NowPlayling.py
```

## FixReport 🔧

Since my playlist [Hard DNB 🔥](https://open.spotify.com/playlist/57VYcWAMIc97Ig41vPpev6) is being reported like _crazy_ and I always have to reset the title, description and reupload the playlist's cover image, i built a script, that would to it automa for me. Screw Spotify's support...

update: my playlist got deleted along with my account. I love spotify :)

## Examples

### Example Lofi

```powershell
python LoFi.py
```

### Example Image

```powershell
python Image.py spotify:playlist:5h9LqGUUE4FKQfVwgAu1OA
```

### Example DailySong

```powershell
python DailySong.py
```

### Example Dubstep

```powershell
python Dubstep.py
```

### Example Backup

```powershell
# requires a gist with a file called "autofy.json" see above
python Backup.py
```

## Setup

### Requirements

- `python`
  - `discord.py`
  - `Pillow`
  - `pyGithub`
  - `pytz`
  - `spotipy`
  - `telethon`

Create a [Telegram application](https://my.telegram.org/)

Create a [Spotify application](https://developer.spotify.com/dashboard/)

Create a [Discord bot](https://discord.com/developers)

Get your [gist token](https://github.com/settings/tokens/new)

Rename `config_template.py` to `config.py`.
Save your api hashes and id's to `config.py`

Install [Python](https://www.python.org/downloads)

Open Powershell/CMD/bash and run the following commands:

```powershell
# if you are unfamiliar with virtual environments, you can read up on them here:
# https://docs.python.org/3/tutorial/venv.html

pip install -U virtualenv, pip

python -m virtualenv venv

./venv/Scripts/activate.ps1

pip install -r requirements.txt
```

Now you can run a script manually like so:

```powershell
# 'xxxxxxxxxx' is the playlist id
python Image.py spotify:playlist:xxxxxxxxxx
```
