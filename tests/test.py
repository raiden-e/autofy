import datetime
import time
import unittest

import DailySong
import spotipy
from telethon import TelegramClient, sync
from util import playlist
from util.spotify import get_spotify_client
from util.telegram import get_telegram_client


class unit_tests(unittest.TestCase):
    def test_telegramClient(self):

        _telegram = get_telegram_client()

        self.assertIsInstance(_telegram, TelegramClient)
        self.assertIsNotNone(_telegram.api_hash)
        self.assertIsNotNone(_telegram.api_id)
        # self.assertTrue(_telegram._authorized)

    def test_get_spotify_client(self):
        _spotify = get_spotify_client()

        self.assertIsNotNone(_spotify)
        self.assertIsInstance(_spotify, spotipy.client.Spotify)

    def test_isTwelvePM_datetime(self):
        DateLike = float, datetime.datetime, datetime.date, datetime.timedelta
        self.assertIn(type(DailySong.get_twelve_pm()), DateLike)

    def test_testingOff(self):
        self.assertFalse(DailySong.test)

    def test_zget_playlist(self):
        def timer_wrapper(func, *args, **kwargs):
            def wrapped():
                tic = time.perf_counter()
                x = func(*args, **kwargs)
                print(f"{func.__name__}: {time.perf_counter() - tic:0.4f}")
                return x
            return wrapped()

        print("")
        _spotify = get_spotify_client()

        args = (
            _spotify,
            "31k9ZXIfUi9v5mpbfg6FQH",
            True
        )

        got_sync = timer_wrapper(playlist.get, *args)
        got_async = timer_wrapper(playlist.getAsync, *args)

        self.assertIsNotNone(got_sync)
        self.assertIsNotNone(got_async)

        sync_list, async_list = [], []
        for x in got_async['items']:
            async_list.append(x['track']['id'])

        for x in got_sync['items']:
            sync_list.append(x['track']['id'])

        self.assertEqual(set(sync_list), set(async_list))
        self.assertRaises(Exception, playlist.get)


if __name__ == '__main__':
    unittest.main()
