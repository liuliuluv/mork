from typing import cast
from discord import Guild, Role, TextChannel, Thread
from discord.utils import get
from discord.ext import commands
import random
from datetime import datetime, timezone, timedelta
from acceptCard import acceptCard

from shared_vars import intents
from secrets.discord_token import DISCORD_ACCESS_TOKEN
import hc_constants

class MyBot(commands.Bot):
    async def setup_hook(self):
        print('This is asynchronous!')

        initial_extensions = [
            'cogs.General',
            'cogs.HellscubeDatabase',
             'cogs.Lifecycle',
             'cogs.Quotes',
             'cogs.Roles',
         'cogs.SpecificCards'
            #   'cogs.Misc'
          ]
        for i in initial_extensions:
            await self.load_extension(i)

bot = MyBot(command_prefix = '!', case_insensitive = True, intents=intents)
bot.remove_command('help')

def getCardMessage(acceptanceMessage:str):
    dbname = ""
    card_author = ""
    if (len(acceptanceMessage)) == 0 or ("by " not in acceptanceMessage):
        ... # This is really the case of setting both to "", but due to scoping i got lazy
    elif (acceptanceMessage[0:3] == "by "):
        card_author = str((acceptanceMessage.split("by "))[1])
    else:
        [firstPart, secondPart] = acceptanceMessage.split(" by ")
        dbname = str(firstPart)
        card_author = str(secondPart)

    resolvedName = dbname if dbname !="" else "Crazy card with no name"
    resolvedAuthor = card_author if card_author != "" else "no author"

    return f"**{resolvedName}** by **{resolvedAuthor}**"



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





@bot.command()
async def compileveto(ctx: commands.Context):
    if ctx.channel.id != hc_constants.VETO_DISCUSSION_CHANNEL:
        await ctx.send("Veto Council Only")
        return

    vetoChannel = cast(TextChannel, bot.get_channel(hc_constants.VETO_CHANNEL))
    vetoDiscussionChannel = cast(TextChannel, bot.get_channel(hc_constants.VETO_DISCUSSION_CHANNEL))
    timeNow = datetime.now(timezone.utc)        
    fourWeeksAgo = timeNow + timedelta(days=-28)
    epicCatchphrases = ["If processing lasts more than 5 minutes, consult your doctor.", "on it, yo.", "ya ya gimme a sec", "processing...", "You're not the boss of me", "ok, 'DAD'", "but what of the children?", "?", "workin' on it!", "on it!", "can do, cap'n!", "raseworter pro tip: run it back, but with less 'tude next time.", "who? oh yeah sure thing b0ss", "how about no for a change?", "CAAAAAAAAAAAAAAN DO!", "i'm afraid i can't let you do that.", "i mean like, if you say so, man", "WOOOOOOOOOOOOOOOOOOOOOOOOOOOO", "*nuzzles u*"]
    
    await ctx.send(random.choice(epicCatchphrases))
    
    
    messages = vetoChannel.history(after = fourWeeksAgo, limit = None)
   
    if messages is None:
        return
    messages = [message async for message in messages]
    acceptedCards:list[str] = []
    errataedCards:list[str] = []
    vetoedCards:list[str] = []
    vetoHellCards:list[str] = []
    for messageEntry in messages:
        if (len(messageEntry.attachments) == 0):
            continue
        up = get(messageEntry.reactions, emoji = hc_constants.VOTE_UP)
        upvote = up.count if up else -1

        down = get(messageEntry.reactions, emoji = hc_constants.VOTE_DOWN)
        downvote = down.count if down else -1

        erratas = get(messageEntry.reactions, emoji = bot.get_emoji( hc_constants.CIRION_SPELLING))
        errata = erratas.count if erratas else -1
       
        messageAge = timeNow - messageEntry.created_at

        # at this point we assume that everything is good


        if get(messageEntry.reactions, emoji = hc_constants.ACCEPT) or get(messageEntry.reactions, emoji = hc_constants.DELETE):
            continue # Skip this card if it has been accepted or deleted. At some point maybe drop the elif here, cause continue skips the rest of the loop
        elif (messageAge < timedelta(days=1)):
            ... # No judgement within the first day

        # Errata needed case
        elif (errata > 4
                and errata >= upvote
                and errata >= downvote):
            errataedCards.append(getCardMessage(messageEntry.content))

            await messageEntry.add_reaction(hc_constants.ACCEPT)
            thread =  cast(Guild, messageEntry.guild).get_channel_or_thread(messageEntry.id)
            if thread:
                await cast(Thread, thread).edit(archived = True)

        # Accepted case
        elif (upvote > 4
                and upvote >= downvote
                and upvote >= errata):
            
            thread = cast(Thread, cast(Guild, messageEntry.guild).get_channel_or_thread(messageEntry.id))
            if thread:
                await thread.edit(archived = True)

            file = await messageEntry.attachments[0].to_file()
            
            acceptanceMessage = messageEntry.content
            # consider putting most of this into acceptCard
            # this is pretty much the same as getCardMessage but teasing out the db logic too was gonna suck
            dbname = ""
            card_author = ""
            if (len(acceptanceMessage)) == 0 or "by " not in acceptanceMessage:
                ... # This is really the case of setting both to "", but due to scoping i got lazy
            elif (acceptanceMessage[0:3] == "by "):
                card_author = str((acceptanceMessage.split("by "))[1])
            else:
                [firstPart, secondPart] = acceptanceMessage.split(" by ")
                dbname = str(firstPart)
                card_author = str(secondPart)
            resolvedName = dbname if dbname !="" else "Crazy card with no name"
            resolvedAuthor = card_author if card_author != "" else "no author"
            cardMessage = f"**{resolvedName}** by **{resolvedAuthor}**"
            acceptedCards.append(cardMessage)
            await acceptCard(
                bot = bot,
                file = file,
                cardMessage = cardMessage,
                cardName = dbname,
                authorName = card_author
            )
            await messageEntry.add_reaction(hc_constants.ACCEPT)


        # Veto case
        elif (downvote > 4 and downvote >= upvote and downvote >= errata):
            vetoedCards.append(getCardMessage(messageEntry.content))
            await messageEntry.add_reaction(hc_constants.ACCEPT) # see ./README.md TODO: maybe use the delete emoji instead?

        # Veto Hell
        elif (messageAge > timedelta(days=3)):
            thread = cast(Thread, cast(Guild,messageEntry.guild).get_channel_or_thread(messageEntry.id))
            role = cast(Role, get(cast(Guild,messageEntry.guild).roles, id = hc_constants.VETO_COUNCIL_MAYBE))
            await thread.send(role.mention)
            vetoHellCards.append(getCardMessage(messageEntry.content))

    await vetoDiscussionChannel.send(content= f"!! VETO POLLS HAVE BEEN PROCESSED !!")

    # had to use format because python doesn't like \n inside template brackets
    if(len(acceptedCards) > 0):
        print("\n\nACCEPTED CARDS: \n{0}".format("\n".join(acceptedCards)))
        await vetoDiscussionChannel.send(content = "\n\nACCEPTED CARDS: \n{0}".format("\n".join(acceptedCards)))
    if(len(errataedCards) > 0):
        print("\n\nNEEDS ERRATA: \n{0}".format("\n".join(errataedCards)))
        await vetoDiscussionChannel.send(content = "\n\nNEEDS ERRATA: \n{0}".format("\n".join(errataedCards)))
    if(len(vetoedCards) > 0):
        print("\n\nVETOED: \n{0}".format("\n".join(vetoedCards)))
        await vetoDiscussionChannel.send(content = "\n\nVETOED: \n{0}".format("\n".join(vetoedCards)))
    if(len(vetoHellCards) > 0):
        print("\n\nVETO HELL: \n{0}".format("\n".join(vetoHellCards)))
        await vetoDiscussionChannel.send(content = "\n\nVETO HELL: \n{0}".format("\n".join(vetoHellCards)))


bot.run(DISCORD_ACCESS_TOKEN)
