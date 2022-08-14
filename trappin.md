<img src="https://i.scdn.co/image/ab67706c0000bebb7659e7adfd8620214114ddbe" alt="trappin" width="200" align="right"/>

<h1 style="margin-top: 0px;">Trappin in Japan</h1>

> Screw spotify for banning my [old account](https://open.spotify.com/user/raiden_e). *RIP*

## For those who wonder what the first song is

[Øfdream - Game Is On](https://youtu.be/F3PluM_H03k)

## So my playlist goes through a process.

I have a playlist called [TRAPPIN IN JPN 🎌.backup](https://open.spotify.com/playlist/0M9SjFcNecW4XlDUSHTIRA) which is a playlist that *more or less* imports a couple of other playlists i found on Spotify.

I also have a playlist with my favorite songs and a gist with songs I wish to be not be included in the weekly mix.

i wrote a [python-script](https://github.com/raiden-e/autofy), that automatically does the following:

```mmd
flowchart
    fav1[Favorite Trap Songs] --> favpool[Favorites]
    fav2[Favorite Phonk Songs] --> favpool
    bak1[Phonk.backup] --> pool[Song pool]
    bak2[Trap.backup] --> pool
    pool -- Reduce to 250 minus fav amount--> pool1[Song pool]
    favpool --> pool1
    pool1 -- Randomize--> pool2[Song pool]
```

1. Grab the favorites playlist.
2. grab the `Backup` and exlude songs that are also in the `gist`
3. from the remaining, choose 250 - `the amount of favorites` songs
4. Randomize the total 250, while leaving one favorite at the top
5. Post to [Spotify](https://open.spotify.com/playlist/0DBoAeAcD19yxfm3VkG3K9)

Hope you enjoy!
