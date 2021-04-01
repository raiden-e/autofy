import datetime
import json
import os
import random
import time
from time import strftime

import pytz
from telethon import functions

from util import playlist
from util.dc import send_webhook
from util.spotify import get_spotify_client
from util.telegram import get_telegram_client


def get_twelve_pm():
    cest = pytz.timezone('Europe/Berlin')

    now = datetime.datetime.now(tz=cest)
    if now.hour >= 12:
        return datetime.timedelta(0)
    else:
        twelve_pm = datetime.datetime(
            now.year, now.month, now.day, 12, tzinfo=cest)
        print(now)
        print(twelve_pm)
        print(twelve_pm - now)
        return twelve_pm - now - datetime.timedelta(minutes=7)


def get_todays_tracks(Data):
    _spotify = get_spotify_client()
    tracks = []
    for pl in Data['TrackDesTages'][strftime("%w")]['get']:
        print(f"loading {pl}")
        tracks.extend(playlist.getAsync(_spotify, pl, True)['items'])
    return tracks


async def message_sent_today():
    result = await client(functions.messages.GetScheduledHistoryRequest(
        peer='TrackDesTages',
        hash=0
    ))
    if result.count != 0:
        print("Todays Track scheduled and will be sent at 12pm")
        return True

    lastMsg = None  # if chat is empty, prevent exeption
    async for lastMsg in client.iter_messages('TrackDesTages', limit=1):
        print(f"Message Date: {lastMsg.date.date()}")
    print(f"Current Date: {datetime.datetime.now().date()}")

    try:
        if test:
            print("Test Mode")
            return True

        # only send message the day after last sent message
        if datetime.datetime.now().date() <= lastMsg.date.date():
            print("Todays Track has alredy been sent")
            return True
    except:
        print("Chat is empty, sending first daily track")

    return False


def get_random(tracks):
    Track = None
    i = 0
    while not Track and i < 100:
        i = i+1
        tmpTrack = random.choice(tracks)["track"]
        try:
            print(tmpTrack['artists'][0]['external_urls']['spotify'])
            print(tmpTrack['external_urls']['spotify'])
            Track = tmpTrack
        except Exception as e:
            print(type(e))
            print(e)

    return Track


def load_data():
    dailysong_texts = os.path.join(
        os.path.dirname(__file__), "util", "dailysong.json")
    try:
        with open(dailysong_texts, "r", encoding='utf-8-sig') as f:
            return json.loads(f.read())
    except(FileNotFoundError, FileExistsError) as e:
        print(f"File not found!\n{e}")
        return False


async def main():
    print("Day of the week: " + str(strftime("%w")))

    if await message_sent_today():
        return 0

    Data = load_data()
    if not Data:
        raise("Couldnt load Data, does dailysong.json exist?")

    print("Loading playlist...")
    tic = time.perf_counter()
    tracks = get_todays_tracks(Data)
    print(f"Loaded playlist(s) in {time.perf_counter() - tic:0.4f} seconds")

    Track = get_random(tracks)
    print(f"DailySong: {Track['name']}")

    messages = (
        {
            "recipiant": 'TrackDesTages',
            "message": f"{Data['TrackDesTages'][strftime('%w')]['DE']}\n\n"
            f"Hier ist [{Track['name']}]"
            f"({Track['external_urls']['spotify']}) von "
            f"[{Track['artists'][0]['name']}]"
            f"({Track['artists'][0]['external_urls']['spotify']})"
        }, {
            "recipiant": 'Daily_Track',
            "message": f"{Data['TrackDesTages'][strftime('%w')]['EN']}\n\n"
            f"This is [{Track['name']}]"
            f"({Track['external_urls']['spotify']}) by "
            f"[{Track['artists'][0]['name']}]"
            f"({Track['artists'][0]['external_urls']['spotify']})"
        }
    )
    if test:
        print("Test Mode: not sending")
    else:
        print("Sending")
        await send_webhook(messages[0]['message'], 'Daily Song')
        async with client:
            for message in messages:
                print(f"sending song to {message['recipiant']}")
                await client.send_message(
                    'me' if test else message['recipiant'],
                    message['message'],
                    schedule=get_twelve_pm()
                )


test = False
test = True

if __name__ == "__main__":
    with get_telegram_client() as client:
        client.loop.run_until_complete(main())
