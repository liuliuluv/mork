import asyncio
from datetime import date, datetime
import os
import random
import aiohttp
from discord import  Member, RawReactionActionEvent, Role, Thread
import discord
from discord.ext import commands
from discord.message import Message
from discord.utils import get
from CardClasses import Card

from checkErrataSubmissions import checkErrataSubmissions
from checkSubmissions import checkSubmissions

from cogs.HellscubeDatabase import searchFor
import hc_constants
from is_mork import is_mork, reasonableCard
from printCardImages import print_card_images
from reddit_functions import postToReddit
from shared_vars import intents,cardSheet,allCards

ONE_HOUR = 3600


client = discord.Client(intents=intents)
bannedUserIds = []

class LifecycleCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # global log
        print(f'{self.bot.user.name} has connected to Discord!')
        nameList = cardSheet.col_values(1)[3:]
        imgList = cardSheet.col_values(2)[3:]
        creatorList = cardSheet.col_values(3)[3:]
        global allCards # Need to modify shared allCards object
        
        for i in range(len(nameList)):
            allCards[nameList[i].lower()] = Card(nameList[i], imgList[i], creatorList[i])
        self.bot.loop.create_task(status_task(self.bot))
        while True:
            await asyncio.sleep(ONE_HOUR)
            # with open("log.txt", 'a', encoding='utf8') as file:
            #     file.write(log)
            #     log = ""
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload:RawReactionActionEvent):
        # global log
        if payload.channel_id == hc_constants.SUBMISSIONS_CHANNEL:
            serv = self.bot.get_guild(hc_constants.SERVER_ID)
            user = serv.get_member(payload.user_id)
            # log += f"{payload.message_id}: Removed {payload.emoji.name} from {payload.user_id} ({user.name}|{user.nick}) at {datetime.now()}\n"

    @commands.Cog.listener()
    async def on_member_join(self,member:Member):
        await member.send(f"Hey there! Welcome to HellsCube. Obligatory pointing towards <#{hc_constants.RULES_CHANNEL}>, <#{hc_constants.FAQ_CHANNEL}> and <#{hc_constants.RESOURCES_CHANNEL}>. Especially the explanation for all our channels and bot command to set your pronouns. Enjoy your stay!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction:RawReactionActionEvent):
        if str(reaction.emoji) == hc_constants.DELETE and not is_mork(reaction.user_id):
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
    async def on_thread_create(self, thread:Thread):
        try:
           await thread.join()
        except:
            print("Can't join that thread.")

    @commands.Cog.listener()
    async def on_message(self,message:Message):
        if (message.author == client.user
            or message.author.bot
            or message.author.id in bannedUserIds):
            return
        if "{{" in message.content:
            await print_card_images(message)
        if message.channel.id == hc_constants.HELLS_UNO_CHANNEL:
            await message.add_reaction(hc_constants.VOTE_UP)
            await message.add_reaction(hc_constants.VOTE_DOWN)
        if message.channel.id == hc_constants.VETO_CHANNEL:
            await message.add_reaction(hc_constants.VOTE_UP)
            await message.add_reaction(self.bot.get_emoji(hc_constants.CIRION_SPELLING))
            await message.add_reaction(hc_constants.VOTE_DOWN)
            await message.add_reaction(self.bot.get_emoji(hc_constants.MANA_GREEN))
            await message.add_reaction(self.bot.get_emoji(hc_constants.MANA_WHITE))
            await message.add_reaction("🤮")
            await message.add_reaction("🤔")
            thread = await message.create_thread(name = message.content[0:99])
            role:Role = get(message.author.guild.roles, id = hc_constants.VETO_COUNCIL_MAYBE)
            await thread.send(role.mention)
        if message.channel.id == hc_constants.FOUR_ZERO_ERRATA_SUBMISSIONS_CHANNEL:
            if "@" in message.content:
                # No ping case
                user = await self.bot.fetch_user(message.author.id)
                await user.send('No "@" are allowed in card title submissions to prevent me from spamming')
                return # no pings allowed
            sentMessage = await message.channel.send(content = message.content)
            await sentMessage.add_reaction(hc_constants.VOTE_UP)
            await sentMessage.add_reaction(hc_constants.VOTE_DOWN)
            await message.delete()
        if message.channel.id == hc_constants.SUBMISSIONS_CHANNEL and len(message.attachments) > 0:
            if "@" in message.content:
                # No ping case
                user = await self.bot.fetch_user(message.author.id)
                await user.send('No "@" are allowed in card title submissions to prevent me from spamming')
                return # no pings allowed
            file = await message.attachments[0].to_file()
            if reasonableCard():
                vetoChannel = self.bot.get_channel(hc_constants.VETO_CHANNEL)
                acceptedChannel = self.bot.get_channel(hc_constants.SUBMISSIONS_DISCUSSION_CHANNEL)
                logChannel = self.bot.get_channel(hc_constants.MORK_SUBMISSIONS_LOGGING_CHANNEL)
                acceptContent = message.content + " was accepted"
                mention = f'<@{str(message.raw_mentions[0])}>'
                accepted_message_no_mentions = message.content.replace(mention, message.mentions[0].name)
                copy = await message.attachments[0].to_file()
                await vetoChannel.send(content=accepted_message_no_mentions, file=copy)
                copy2 = await message.attachments[0].to_file()
                logContent = f"{acceptContent}, message id: {message.id}, upvotes: 0, downvotes: 0, magic: true"
                await acceptedChannel.send(content = "✨✨ {acceptContent} ✨✨")
                await acceptedChannel.send(content = "", file = file)
                await logChannel.send(content=logContent, file = copy2)
            else:
                sentMessage = await message.channel.send(content = f"{message.content} by {message.author.mention}" , file = file)
                await sentMessage.add_reaction(hc_constants.VOTE_UP)
                await sentMessage.add_reaction(hc_constants.VOTE_DOWN)
                await sentMessage.add_reaction(hc_constants.DELETE)
            await message.delete()

async def setup(bot:commands.Bot):
    await bot.add_cog(LifecycleCog(bot))



FIVE_MINUTES = 300

async def status_task(bot:commands.Bot):
    while True:
        # creator = random.choice(cardSheet.col_values(3)[4:])
        status = random.choice(hc_constants.statusList)
        # print(status)
        await checkSubmissions(bot)
        await checkErrataSubmissions(bot)
        await bot.change_presence(status = discord.Status.online, activity = discord.Game(status))
        now = datetime.now()
        print(f"time is {now}")
        if now.hour == 4 and now.minute <= 5:
            nowtime = now.date()
            start = date(2024,3,16)
            days_since_starting = (nowtime - start).days
            cardOffset = 608 - days_since_starting
            if cardOffset >= 0:
                cards = searchFor({"cardset":"hc4"})
                card = cards[cardOffset]
                name = card.name()
                url = card.img()
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            print(resp)                       
                            image_path = f'tempImages/{name}'
                            with open(image_path, 'wb') as out: ## Open temporary file as bytes
                                out.write(await resp.read())  ## Read bytes into file
                            try:
                                await  postToReddit(
                                    title = f"HC4 Card of the ~day: {name}",
                                    image_path=image_path,
                                    flair="5778f0e4-52c0-11eb-9a1d-0ebf18b4acab"
                                )
                            except:
                                ...
                            os.remove(image_path)
        await asyncio.sleep(FIVE_MINUTES)
