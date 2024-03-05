import random
import discord
from discord.ext import commands
from random import randrange

from datetime import datetime, timezone, timedelta
import hc_constants
from sendImage import sendImage


from shared_vars import intents,allCards

client = discord.Client(intents=intents)



class HellscubeDatabaseCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
    
    # okay not technically a DB command
    @commands.command()
    async def randomReject(self, channel, num=0):
        """
        Returns a random card image from #submissions.
        Chooses a random date between the start of submissions and now, then gets history near that date.
        Chooses a random message from that history. If chosen message has no image, calls itself up to 9 more times.
        """
        if num > 9:
            await channel.send("Sorry, no cards were found.")
            return
        subStart = datetime.strptime('5/13/2021 1:30 PM', '%m/%d/%Y %I:%M %p')
        timeNow = datetime.now(timezone.utc)
        timeNow = timeNow.replace(tzinfo=None)
        delta = timeNow - subStart
        intDelta = (delta.days * 24 * 60 * 60) + delta.seconds
        randomSecond = randrange(intDelta)
        randomDate = subStart + timedelta(seconds=randomSecond)
        subChannel = self.bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
        subHistory = subChannel.history(around = randomDate)
        subHistory = [message async for message in subHistory]
        randomNum = randrange(1, len(subHistory)) - 1
        if len(subHistory[randomNum].attachments) > 0:
            file = await subHistory[randomNum].attachments[0].to_file()
            await channel.send(content = "", file = file)
        else:
            num += 1
            command = self.bot.get_command("randomReject")
            await channel.invoke(command, num)

    @commands.command(name="random")
    async def randomCard(channel):
        card = allCards[random.choice(list(allCards.keys()))]
        await sendImage(card.getImg(), card.getName(), channel)

async def setup(bot:commands.Bot):
    await bot.add_cog(HellscubeDatabaseCog(bot))