import io
import aiohttp
import discord
from cardNameRequest import cardNameRequest
import hc_constants
from shared_vars import allCards

async def printCardImages(message):
  messageText = message.content.lower().split("{{")[1:]
  for i in range(len(messageText)):
    messageText[i] = messageText[i].split("}}")[0]
  requestedCards = []
  if len(messageText) > 10 and message.author.id != hc_constants.CIRION:
    await message.reply("Don't call more than 10 cards per message, final warning, keep trying and you get blacklisted from the bot. Blame dRafter for this if you're actually trying to use the bot.")
    return
  for cardName in messageText:
    requestedCards.append(await cardNameRequest(cardName))
  for post in requestedCards:
    if post == "":
      await message.reply("No Match Found!", mention_author=False)
    else:
      await sendImageReply(allCards[post].getImg(), allCards[post].getName(), message)


async def sendImageReply(url, cardname, message):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      if resp.status != 200:
        await message.reply('Something went wrong while getting the link for ' + cardname + '. Wait for @exalted to fix it.')
        return
      data = io.BytesIO(await resp.read())
      sentMessage = await message.reply(file=discord.File(data, url), mention_author=False)
      await sentMessage.add_reaction("❌")


