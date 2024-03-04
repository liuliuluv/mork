from discord import RawReactionActionEvent
from discord.ext import commands
from discord.message import Message

import hc_constants
import is_mork

class LifecycleCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_message(self, message:Message):
    #     print(message.channel.id)
    #     if message.channel.id == hc_constants.BOT_TEST_CHANNEL:
    #         print(message)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload:RawReactionActionEvent):
        # debug
        return
        global log
        if payload.channel_id == hc_constants.SUBMISSIONS_CHANNEL:
            serv = self.bot.get_guild(hc_constants.SERVER_ID)
            user = serv.get_member(payload.user_id)
            log += f"{payload.message_id}: Removed {payload.emoji.name} from {payload.user_id} ({user.name}|{user.nick}) at {datetime.now()}\n"

    @commands.Cog.listener()
    async def on_member_join(member):
        await member.send(f"Hey there! Welcome to HellsCube. Obligatory pointing towards <#{hc_constants.RULES_CHANNEL}>, <#{hc_constants.FAQ}> and <#{hc_constants.RESOURCES_CHANNEL}>. Especially the explanation for all our channels and bot command to set your pronouns. Enjoy your stay!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,reaction:RawReactionActionEvent):
        # debug
        return
        if str(reaction.emoji) == "❌" and not is_mork(reaction.user_id):
            guild = self.bot.get_guild(reaction.guild_id)
            channel = guild.get_channel(reaction.channel_id)
            message = await channel.fetch_message(reaction.message_id)
            if reaction.member in message.mentions and is_mork(message.author.id):
                await message.delete()
                return
            if message.reference:
                messageReference = await channel.fetch_message(message.reference.message_id)
                if reaction.member == messageReference.author and is_mork(message.author.id):
                    await message.delete()
                    return

    @commands.Cog.listener()
    async def on_thread_create(thread):
        try:
           await thread.join()
        except:
            print("Can't join that thread.")


    @commands.Cog.listener()
    async def on_ready(self):
        global log
        print(f'{self.bot.user.name} has connected to Discord!')
        # debug 
        return
        nameList = cardSheet.col_values(1)[3:]
        imgList = cardSheet.col_values(2)[3:]
        creatorList = cardSheet.col_values(3)[3:]
        global allCards # Need to modify shared allCards object
        for i in range(len(nameList)):
            allCards[nameList[i].lower()] = Card(nameList[i], imgList[i], creatorList[i])
        bot.loop.create_task(status_task())
        while True:
            await asyncio.sleep(3600)
            with open("log.txt", 'a', encoding='utf8') as file:
                file.write(log)
                log = ""

async def setup(bot:commands.Bot):
    await bot.add_cog(LifecycleCog(bot))