
import discord
from discord.ext import commands
from discord.utils import get



from shared_vars import intents,cardSheet,allCards


client = discord.Client(intents=intents)

class MiscCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     global log
    #     print(f'{self.bot.user.name} has connected to Discord!')
    #     vetoChannel = self.bot.get_channel(hc_constants.VETO_CHANNEL)

       
    #     messages = vetoChannel.history( limit=4 )
    #     # messages = [message async for message in messages]
    #     # for message in messages:
    #     #     if message.content == "EXACT SUBJECT":
    #     #         print(message.content)
    #     #        # await message.delete()

    # @commands.command()
    # async def modal(self, ctx:commands.Context):
    #    print(ctx.interaction)
    #    await ctx.interaction.response.send_modal(MorkModal())
        


async def setup(bot:commands.Bot):
    await bot.add_cog(MiscCog(bot))



class MorkModal(
    discord.ui.Modal,title="testing"
):
    discord.ui.TextInput(
        label='Name',
        placeholder='Your name here...',
    )
    async def on_submit(self, interaction: discord.Interaction):
        print('!')

