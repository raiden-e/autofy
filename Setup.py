from setuptools import setup

test_reqs = [
]
extra_reqs = {
}
setup(
    name='autofy',
    version='1.0.1',
    description='A script to backup Spotify playlists; send\'s a daily track and set a lofi playlist weekly',
    author="@raiden-e",
    author_email="raiden.erdmann@gmail.com",
    install_requires=[
        'spotipy',
        'telethon'
        'discord.py'
    ],
    tests_require=test_reqs,
    extras_require=extra_reqs,
    test_suite='setup.my_test_suite',
)
