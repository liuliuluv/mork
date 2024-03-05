# send card image to channel
import io
import aiohttp
import discord


async def sendImage(url, cardname, channel):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      if resp.status != 200:
        await channel.send('Something went wrong while getting the link for ' + cardname + '. Wait for @exalted to fix it.')
        return
      data = io.BytesIO(await resp.read())
      await channel.send(file=discord.File(data, url))