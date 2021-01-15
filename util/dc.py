import asyncio

import aiohttp
import config
import discord

webhook_url = f"https://discordapp.com/api/webhooks/{config.DCGUILD}/{config.DCTOKEN}"


async def send_webhook(message, username):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(
            webhook_url, adapter=discord.AsyncWebhookAdapter(session))
        await webhook.send(message, username=username)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    my_loop = loop.create_task(send_webhook("Test Message"))
    loop.run_until_complete(my_loop)
