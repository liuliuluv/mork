import discord
from discord.utils import get
from discord.ext import commands
import asyncio
import random
import gspread
from datetime import datetime, timezone, timedelta
from reddit_functions import postToReddit
from checkErrataSubmissions import checkErrataSubmissions

from shared_vars import intents,googleClient,drive
import is_mork
from secrets.discord_token import DISCORD_ACCESS_TOKEN
import hc_constants

class MyBot(commands.Bot):
    async def setup_hook(self):
        print('This is asynchronous!')
        initial_extensions = [
     #     'cogs.SpecificCards',
     #     'cogs.Roles',
          'cogs.Lifecycle',
      #    'cogs.ZaxersKisses',
      #    'cogs.Quotes',
      #    'cogs.HellscubeDatabase'
      #     'cogs.General
          ]
        for i in initial_extensions:
            await self.load_extension(i)

bot = MyBot(command_prefix='!', case_insensitive=True, intents=intents)
bot.remove_command('help')


@bot.command()
async def check_cogs(ctx:commands.Context, cog_name):
    try:
        await bot.load_extension(f"cogs.{cog_name}")
    except commands.ExtensionAlreadyLoaded:
        await ctx.send("Cog is loaded")
    except commands.ExtensionNotFound:
        await ctx.send("Cog not found")
    else:
        await ctx.send("Cog is unloaded")
        await bot.unload_extension(f"cogs.{cog_name}")


cardSheetUnapproved = googleClient.open_by_key(hc_constants.HELLSCUBE_DATABASE).get_worksheet(1)


async def checkSubmissions():
    subChannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
    vetoChannel = bot.get_channel(hc_constants.VETO_CHANNEL)
    acceptedChannel = bot.get_channel(hc_constants.SUBMISSIONS_DISCUSSION_CHANNEL)
    logChannel = bot.get_channel(hc_constants.MORK_SUBMISSIONS_LOGGING_CHANNEL)
    timeNow = datetime.now(timezone.utc)
    oneWeek = timeNow + timedelta(weeks=-1)
    messages = subChannel.history(after=oneWeek, limit=None)
    if messages is None:
        return
    messages = [message async for message in messages]
    for messageEntry in messages:
      if "@everyone" in messageEntry.content:
        continue # uhhhhh what is this
      upvote = get(messageEntry.reactions, emoji=hc_constants.VOTE_UP)
      downvote = get(messageEntry.reactions, emoji=hc_constants.VOTE_DOWN)
      if upvote and downvote:
        upCount = upvote.count
        downCount = downvote.count
        messageAge = timeNow - messageEntry.created_at
        # card was voted in
        if (upCount - downCount) > 24 and len(messageEntry.attachments) > 0 and messageAge >= timedelta(days=1) and is_mork.is_mork(messageEntry.author.id):
          if downCount == 1:
            user = await bot.fetch_user(hc_constants.EXALTED_ONE) # I'm assuming this was to avoid spam
            await user.send("Verify " + messageEntry.jump_url)
            continue
          file = await messageEntry.attachments[0].to_file()
          copy = await messageEntry.attachments[0].to_file()
          copy2 = await messageEntry.attachments[0].to_file()
          acceptContent = messageEntry.content + " was accepted "
          mention = f'<@{str(messageEntry.raw_mentions[0])}>'
          nickMention = f'<@{str(messageEntry.raw_mentions[0])}>'
          removeMention = messageEntry.content.replace(mention, "")
          removeMention = removeMention.replace(nickMention, "")
          vetoContent = removeMention + messageEntry.mentions[0].name
          logContent = f"{acceptContent}, message id: {messageEntry.id}, upvotes: {upCount}, downvotes: {downCount}"
          await acceptedChannel.send(content=acceptContent)
          await acceptedChannel.send(content="", file=file)
          await vetoChannel.send(content=vetoContent, file=copy)
          await logChannel.send(content=logContent, file=copy2)
          await messageEntry.delete()
          continue
    print("------done checking submissions-----")



   

def vetoAnnouncementHelper(cardArray:list[discord.Message], announcement:list[str], annIndex:int):
    for i in cardArray:
        thisLine = i.content
        if len(announcement[annIndex]) + len(thisLine) > 1950:
            announcement.append("")
            annIndex += 1
        if (len(i.content)) == 0:
            announcement[annIndex] += "**Crazy card with no name and no author**\n"
        elif (i.content[0:3] == "by "):
            announcement[annIndex] += f"**Silly card with no name** {i.content}\n"
        else:
            thisLine = thisLine.split(" by ")
            for i in range(len(thisLine)):
                if i == 0:
                    announcement[annIndex] += "**" + thisLine[0] + "**"
                else:
                    announcement[annIndex] += " by " + thisLine[i]
            announcement[annIndex] += "\n"
    return annIndex

@bot.command()
async def compileveto(ctx:commands.Context):
        #debug
        return
        if ctx.channel.id == hc_constants.VETO_DISCUSSION_CHANNEL:
                vetoChannel = bot.get_channel(hc_constants.VETO_CHANNEL)
                vetoDiscussionChannel = bot.get_channel(hc_constants.VETO_DISCUSSION_CHANNEL)
                cardListChannel = bot.get_channel(hc_constants.FOUR_ONE_CARD_LIST_CHANNEL)
                timeNow = datetime.now(timezone.utc)        
                twoWeekAgo = timeNow + timedelta(days=-28)
                epicCatchphrases = ["If processing lasts more than 5 minutes, consult your doctor.", "on it, yo.", "ya ya gimme a sec", "processing...", "You're not the boss of me", "ok, 'DAD'", "but what of the children?", "?", "workin' on it!", "on it!", "can do, cap'n!", "raseworter pro tip: run it back, but with less 'tude next time.", "who? oh yeah sure thing b0ss", "how about no for a change?", "CAAAAAAAAAAAAAAN DO!", "i'm afraid i can't let you do that.", "i mean like, if you say so, man", "WOOOOOOOOOOOOOOOOOOOOOOOOOOOO", "*nuzzles u*"]
                await ctx.send(random.choice(epicCatchphrases))
                messages = vetoChannel.history(after=twoWeekAgo, limit=None)
                print(messages)
                if messages is None:
                        return
                messages = [message async for message in messages]
                acceptedCards:list[discord.Message] = []
                errataedCards:list[discord.Message] = []
                vetoedCards:list[discord.Message] = []
                vetoHell:list[discord.Message] = []
                for messageEntry in messages:
                        try:
                                upvote = get(messageEntry.reactions, emoji=hc_constants.VOTE_UP).count
                        except:
                                upvote = -1
                        try:
                                downvote = get(messageEntry.reactions, emoji=hc_constants.VOTE_DOWN).count
                        except:
                                downvote = -1
                        try:
                                errata = get(messageEntry.reactions, emoji=hc_constants.CIRION_SPELLING).count
                        except:
                                errata = -1
                        if (len(messageEntry.attachments) == 0):
                                continue
                        messageAge = timeNow - messageEntry.created_at

                        # at this point we assume that everything is good

                        if get(messageEntry.reactions, emoji = hc_constants.ACCEPT) or get(messageEntry.reactions, emoji = hc_constants.DENY):
                                continue
                        elif (messageAge < timedelta(days=1)):
                                ... # No idea why this case was here...

                        # Errata needed case
                        elif (errata > 4
                              and errata >= upvote
                              and errata >= downvote):
                                errataedCards.append(messageEntry)
                                await messageEntry.add_reaction(hc_constants.ACCEPT)
                                thread = messageEntry.guild.get_channel_or_thread(messageEntry.id)
                                await thread.edit(archived = True)

                        # Accepted case
                        elif (upvote > 4
                              and upvote >= downvote
                              and upvote >= errata):
                                acceptedCards.append(messageEntry)
                                await messageEntry.add_reaction(hc_constants.ACCEPT)
                                thread = messageEntry.guild.get_channel_or_thread(messageEntry.id)
                                await thread.edit(archived = True)
                                file = await messageEntry.attachments[0].to_file() # lol okay here's the other weird file and copy
                                copy = await messageEntry.attachments[0].to_file()
                                
                                acceptanceMessage = messageEntry.content
                                dbname = ""
                                dbauthor = ""
                                if (len(acceptanceMessage)) == 0:
                                        ... # This is really the case of setting both to "", but due to scoping i got lazy
                                elif (acceptanceMessage[0:3] == "by "):
                                        dbauthor = str((acceptanceMessage.split("by "))[1])
                                else:
                                        [firstPart, secondPart] = acceptanceMessage.split(" by ")
                                        dbname = str(firstPart)
                                        dbauthor = str(secondPart)

                                resolvedName = dbname if dbname !="" else "Crazy card with no name"
                                resolvedAuthor = dbauthor if dbauthor != "" else "no author"
                                sentMessage = await cardListChannel.send(content=f"**{resolvedName}** by **{resolvedAuthor}**", file=copy)

                                try:
                                        postToReddit(file=copy,
                                                     title=f"{resolvedName} by {resolvedAuthor} was accepted!",
                                                     flair=hc_constants.ACCEPTED_FLAIR)
                                except:
                                        ...

                                # here is where we'll need to upload the file to google
                                imageUrl = sentMessage.attachments[0].url
                                allCardNames = cardSheetUnapproved.col_values(1)
                                newCard = True
                                if dbname in allCardNames and dbname != "":
                                        dbRowIndex = allCardNames.index(dbname) + 1
                                        newCard = False
                                else:
                                        dbRowIndex = len(allCardNames) + 1
                                        if dbname == "":
                                                dbname = "NO NAME"
                                cardSheetUnapproved.update_cell(dbRowIndex, 4, imageUrl)
                                if newCard:
                                        # If adding a new card, bold that row
                                        cardSheetUnapproved.update_cell(dbRowIndex, 1, dbname)
                                        cardSheetUnapproved.update_cell(dbRowIndex, 6, dbauthor)
                                        boldRangesA1 = [gspread.utils.rowcol_to_a1(dbRowIndex, 1), gspread.utils.rowcol_to_a1(dbRowIndex, 4), gspread.utils.rowcol_to_a1(dbRowIndex, 6)]
                                        cardSheetUnapproved.format(boldRangesA1, {'textFormat': {'bold': True}})
                                else:
                                        # If editing a card, italic it (see if we can just change this to bold. there's not that meaningful of a difference... i think)
                                        cardSheetUnapproved.format(gspread.utils.rowcol_to_a1(dbRowIndex, 4), {'textFormat': {'bold': True}})
                                        italicsRangesA1 = []
                                        thisRow = cardSheetUnapproved.row_values(dbRowIndex)
                                        print(thisRow)
                                        for i in range(len(thisRow)):
                                                if thisRow[i] != "" and i != 0 and i != 3 and i != 5:
                                                        italicsRangesA1.append(gspread.utils.rowcol_to_a1(dbRowIndex, i + 1))
                                        if italicsRangesA1 != []:
                                                cardSheetUnapproved.format(italicsRangesA1, {'textFormat': {'italic': True}})

                        # Veto case
                        elif (downvote > 4 and downvote >= upvote and downvote >= errata):
                                vetoedCards.append(messageEntry)
                                await messageEntry.add_reaction(hc_constants.ACCEPT) # see ./README.md

                        # Veto Hell
                        elif (messageAge > timedelta(days=3)):
                                thread = messageEntry.guild.get_channel_or_thread(messageEntry.id)
                                role = get(messageEntry.guild.roles, id=hc_constants.VETO_COUNCIL_MAYBE)
                                await thread.send(role.mention)
                                vetoHell.append(messageEntry)


                announcement = [""]
                annIndex = 0
                announcement[annIndex] = "!! VETO POLLS HAVE BEEN PROCESSED !! \n\nACCEPTED CARDS: \n"
                annIndex = vetoAnnouncementHelper(acceptedCards, announcement, annIndex)
                announcement[annIndex] += "\nNEEDS ERRATA: \n"
                annIndex = vetoAnnouncementHelper(errataedCards, announcement, annIndex)
                announcement[annIndex] += "\nVETOED: \n"
                annIndex = vetoAnnouncementHelper(vetoedCards, announcement, annIndex)
                announcement[annIndex] += "\nVETO HELL: \n"
                annIndex = vetoAnnouncementHelper(vetoHell, announcement, annIndex)

##                for vetoedCard in vetoHell:
##                        file = await vetoedCard.attachments[0].to_file()
##                        copy = await vetoedCard.attachments[0].to_file() # i have no idea why the function to repost card messages was coded with this weird "copy" thing. If you're reading this, help.
                ## I'm sorry, i can't help. oh shit i deleted a copy line a while ago. hope we didnit need that
##                        cardMessage = vetoedCard.content
##                        await vetoChannel.send(content=cardMessage, file=copy)

                print(announcement)
                for i in announcement:
                        await vetoDiscussionChannel.send(content=i)

        else:
                await ctx.send("Veto Council Only")


bot.run(DISCORD_ACCESS_TOKEN)
