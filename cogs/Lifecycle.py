from discord import RawReactionActionEvent
from discord.ext import commands
from discord.message import Message

import hc_constants

class LifecycleCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_message(self, message:Message):
    #     print(message.channel.id)
    #     if message.channel.id == hc_constants.BOT_TEST_CHANNEL:
    #         print(message)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(payload:RawReactionActionEvent):
        # debug
        return
        global log
        if payload.channel_id == hc_constants.SUBMISSIONS_CHANNEL:
            serv = bot.get_guild(hc_constants.SERVER_ID)
            user = serv.get_member(payload.user_id)
            log += f"{payload.message_id}: Removed {payload.emoji.name} from {payload.user_id} ({user.name}|{user.nick}) at {datetime.now()}\n"

    @commands.Cog.listener()
    async def on_member_join(member):
        await member.send(f"Hey there! Welcome to HellsCube. Obligatory pointing towards <#{hc_constants.RULES_CHANNEL}>, <#{hc_constants.FAQ}> and <#{hc_constants.RESOURCES_CHANNEL}>. Especially the explanation for all our channels and bot command to set your pronouns. Enjoy your stay!")

async def setup(bot:commands.Bot):
    await bot.add_cog(LifecycleCog(bot))