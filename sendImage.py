# send card image to channel
import io
import aiohttp
import discord


async def send_image(url:str, card_name, channel):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await channel.send('Something went wrong while getting the link for ' + card_name + '. Wait for @llllll to fix it.')
                return
            data = io.BytesIO(await resp.read())
        await channel.send(file=discord.File(data, url))