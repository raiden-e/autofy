import asyncio

import aiohttp
import config
import discord

api_url = "https://discordapp.com/api/webhooks"
webhook_url = f"{api_url}/{config.DISCORD['NEWS_URL']}"
error_log_url = f"{api_url}/{config.DISCORD['ERROR_URLs']}"


async def send_webhook(message, username=None, url=webhook_url):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(session))
        await webhook.send(message, username=username)


async def error_log(message):
    await send_webhook(message, 'ErrorLog', error_log_url)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    my_loop = loop.create_task(send_webhook("Test Message"))
    loop.run_until_complete(my_loop)
