
from datetime import datetime, timedelta, timezone
from typing import cast
import discord
from discord.ext import commands
from discord.utils import get



from acceptCard import acceptCard
import hc_constants
from shared_vars import intents,cardSheet,allCards


client = discord.Client(intents=intents)

class MiscCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot


    # @commands.Cog.listener()
    # async def on_ready(self):
    #     vetoChannel = cast(discord.TextChannel, self.bot.get_channel(hc_constants.VETO_CHANNEL))
    #     # vetoDiscussionChannel = cast(discord.TextChannel, self.bot.get_channel(hc_constants.VETO_DISCUSSION_CHANNEL))
    #     timeNow = datetime.now(timezone.utc)        
    #     fourWeeksAgo = timeNow + timedelta(days=-28)

    #     messages = vetoChannel.history(after = fourWeeksAgo, limit = None)
    
    #     if messages is None:
    #         return
    #     messages = [message async for message in messages]

    #     for messageEntry in messages:
            
    #         guild = cast(discord.Guild, messageEntry.guild)
    #         thread = cast(discord.Thread, guild.get_channel_or_thread(messageEntry.id))
    #         if thread:
    #         # new code
    #             threadMessages = thread.history()
    #             threadMessages = [message async for message in threadMessages]
    #             for threadMessage in threadMessages:
          
    #                 if threadMessage.content == f"<@&{798689768379908106}>":
    #                    if (timeNow - threadMessage.created_at) < timedelta(days = 7):
    #                     # then it was recently acted upon
    #                     print(threadMessage.created_at, messageEntry.content)
            
        # end new code


# Mork Rasewoter#1393
# mork2#8326

    # @commands.Cog.listener()
    # async def on_ready(self):
        






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
        

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print(f'{self.bot.user.name} has connected to Discord!')
    #     cardlist = self.bot.get_channel(hc_constants.FOUR_ONE_CARD_LIST_CHANNEL)
    #     messages = cardlist.history( limit=12 )
    #     messages = [message async for message in messages]
    #     for message in messages:
    #         #print(message.content)
    #         [card,creator]=(message.content.split('** by **'))
    #         card = card.replace("**",'')
    #        # print(card)


    #         creator = creator.replace("**",'')
    #       #  print(creator)

    #         cardMessage=message.content.replace('**','')


    #         file = await message.attachments[0].to_file()
    #         print( cardMessage, file, card, creator)
         



async def setup(bot:commands.Bot):
    await bot.add_cog(MiscCog(bot))



