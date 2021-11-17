# rename this file to config.py

TELEID = ""       # Go to link below
TELEHASH = ""     # https://my.telegram.org/
TELEST = ""       # Telegram string to login to
SPOTIPYID = ""    # Go to link below
SPOTIPYHS = ""    # https://developer.spotify.com/dashboard/
SPOTIPYUN = ""    # Your spotify username
SPOTIPYRU = ""    # The redirect url for spotify login
SPOTIPYCACHE = ""  # basically the same string as in util/spotify.cache
SPOTIPYSC = "ugc-image-upload playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-currently-playing user-top-read user-read-playback-state"
GISTTOKEN = ""    # Go to below link and make sure you check 'gist'
GISTID = ""       # https://github.com/settings/tokens
DCTOKEN = ""      # A discord token to login to ur bot
DCGUILD = ""      # guild id of your server

# A small powershell script to escap when using GitHub actions
#
# $a = Get-Content config.py -Raw -Encoding utf8
# $chars = ("\", '"', "(", ")")
# foreach ($char in $chars) { $a = ($a -replace "\$char", "\$char") }
# $a = ($a -replace "\s*#.*(\n|$)", "`n" -replace "\n{2,}", "`n")
# $a | Out-File config2.py -Encoding utf8
