
import discord
from discord.ext import commands
from discord.utils import get


from cogs.HellscubeDatabase import searchFor
import hc_constants
from is_mork import is_mork, reasonableCard
from printCardImages import print_card_images
from reddit_functions import postToReddit
from shared_vars import intents,cardSheet,allCards

client = discord.Client(intents=intents)

class MiscCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global log
        print(f'{self.bot.user.name} has connected to Discord!')
        vetoChannel = self.bot.get_channel(hc_constants.VETO_CHANNEL)

        messages = vetoChannel.history( limit=4)
        messages = [message async for message in messages]
        for message in messages:
            if message.content == "EXACT SUBJECT":
                print(message.content)
               # await message.delete()


async def setup(bot:commands.Bot):
    await bot.add_cog(MiscCog(bot))

