import asyncio
import io
import os
import re
import aiohttp
from discord import  RawReactionActionEvent
import discord
from discord.ext import commands
from discord.message import Message
from discord.utils import get
from CardClasses import Card
from cardNameRequest import cardNameRequest

import hc_constants
from is_mork import is_mork
from printCardImages import printCardImages
from shared_vars import intents,cardSheet,allCards
from test import postToReddit

ONE_HOUR = 3600


client = discord.Client(intents=intents)
bannedUserIds = []

class LifecycleCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global log
        print(f'{self.bot.user.name} has connected to Discord!')
     
        nameList = cardSheet.col_values(1)[3:]
        imgList = cardSheet.col_values(2)[3:]
        creatorList = cardSheet.col_values(3)[3:]
        global allCards # Need to modify shared allCards object
        for i in range(len(nameList)):
            allCards[nameList[i].lower()] = Card(nameList[i], imgList[i], creatorList[i])
        # debug 
        return
        self.bot.loop.create_task(status_task())
        while True:
            await asyncio.sleep(ONE_HOUR)
            with open("log.txt", 'a', encoding='utf8') as file:
                file.write(log)
                log = ""
        
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
        if str(reaction.emoji) == hc_constants.DENY and not is_mork(reaction.user_id):
            guild = self.bot.get_guild(reaction.guild_id)
            channel = guild.get_channel(reaction.channel_id)
            message = await channel.fetch_message(reaction.message_id)
            if not is_mork(message.author.id):
                return
            if reaction.member in message.mentions:
                await message.delete()
                return
            if message.reference:
                messageReference = await channel.fetch_message(message.reference.message_id)
                if reaction.member == messageReference.author:
                    await message.delete()
                    return

    @commands.Cog.listener()
    async def on_thread_create(thread):
        try:
           await thread.join()
        except:
            print("Can't join that thread.")

    @commands.Cog.listener()
    async def on_message(self,message:Message):
        if (message.author.id == hc_constants.LLLLLL and "XX" in message.content):
            print(message.content)
            card=await cardNameRequest(message.content.replace("XX",""))
            
            url =  allCards[card].getImg()
            print(url)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await message.reply('Something went wrong while getting the link for ' + card + '. Wait for @exalted to fix it.')
                        return
                    # currently extraFilename looks like inline;filename="                                Skald.png"
                    extraFilename = resp.headers.get("Content-Disposition")  
                    parsedFilename = re.findall('inline;filename="(.*)"', extraFilename)[0]
                    data = await resp.read()
 
                    image_path=f'tempImages/{parsedFilename}'
                    with open(image_path,'wb') as out: ## Open temporary file as bytes
                        out.write(data)                ## Read bytes into file

                    await postToReddit(image_path, title=f'{card} was accepted')

                    ## Do stuff with module/file
                    os.remove(image_path) ## Delete file when done
        #debug
        return
        if (message.author == client.user
            or message.author.bot
            or message.author.id in bannedUserIds):
            return
        #if message.channel.id == hc_constants.SUBMISSIONS_CHANNEL and len(message.attachments) > 0:
        #  await message.add_reaction(hc_constants.VOTE_UP)
        #  await message.add_reaction(hc_constants.VOTE_DOWN)
        if message.channel.id == hc_constants.HELLS_UNO_CHANNEL:
            await message.add_reaction(hc_constants.VOTE_UP)
            await message.add_reaction(hc_constants.VOTE_DOWN)
        if message.channel.id == hc_constants.VETO_CHANNEL or message.channel.id == hc_constants.EDH_POLLS_CHANNEL:
            await message.add_reaction(hc_constants.VOTE_UP)
            await message.add_reaction(self.bot.get_emoji(hc_constants.CIRION_SPELLING))
            await message.add_reaction(hc_constants.VOTE_DOWN)
            await message.add_reaction(self.bot.get_emoji(hc_constants.MANA_GREEN))
            await message.add_reaction(self.bot.get_emoji(hc_constants.MANA_WHITE))
            await message.add_reaction("🤮")
            await message.add_reaction("🤔")
            thread = await message.create_thread(name=message.content)
            role = get(message.author.guild.roles, id=int(798689768379908106))
            await thread.send(role.mention)
        ##    for user in role.members:
        ##        await thread.add_user(user)
        ##        await asyncio.sleep(1)
        if message.channel.id == hc_constants.FOUR_ZERO_ERRATA_SUBMISSIONS_CHANNEL:
            if "@" in message.content:
                return
            sentMessage = await message.channel.send(content = message.content)
            await sentMessage.add_reaction(hc_constants.VOTE_UP)
            await sentMessage.add_reaction(hc_constants.VOTE_DOWN)
            await message.delete()
        if message.channel.id == hc_constants.SUBMISSIONS_CHANNEL and len(message.attachments) > 0:
            if "@" in message.content:
                return # I'm confused what this case is, it might be the non-bot case, but who knows
            file = await message.attachments[0].to_file()
            sentMessage = await message.channel.send(content = message.content + " by " + message.author.mention, file = file)
            await sentMessage.add_reaction(hc_constants.VOTE_UP)
            await sentMessage.add_reaction(hc_constants.VOTE_DOWN)
            await sentMessage.add_reaction(hc_constants.DENY)
            await message.delete()
        if "{{" in message.content:
            await printCardImages(message)
        try:
            await self.bot.process_commands(message)
        except:
            ...

async def setup(bot:commands.Bot):
    await bot.add_cog(LifecycleCog(bot))