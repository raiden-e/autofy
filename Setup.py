from setuptools import setup

test_reqs = [
]
extra_reqs = {
}
setup(
    name='Spotify-Helper',
    version='1.0.0',
    description='A script to backup Spotify playlists; send\'s a daily track and set a lofi playlist weekly',
    author="@Omglolyes",
    author_email="raiden.erdmann@gmail.com",
    install_requires=[
        'spotipy',
        'telethon'
        'discord.py'
    ],
    tests_require=test_reqs,
    test_suite='setup.my_test_suite',
    extras_require=extra_reqs,
)
