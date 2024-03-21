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
            'cogs.SpecificCards',
            'cogs.ZaxersKisses'
            # 'cogs.Misc'
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





@bot.command()
async def compileveto(ctx:commands.Context):

    if ctx.channel.id != hc_constants.VETO_DISCUSSION_CHANNEL:
        await ctx.send("Veto Council Only")
        return

    vetoChannel = bot.get_channel(hc_constants.VETO_CHANNEL)
    vetoDiscussionChannel = bot.get_channel(hc_constants.VETO_DISCUSSION_CHANNEL)
    timeNow = datetime.now(timezone.utc)        
    twoWeekAgo = timeNow + timedelta(days=-28)
    epicCatchphrases = ["If processing lasts more than 5 minutes, consult your doctor.", "on it, yo.", "ya ya gimme a sec", "processing...", "You're not the boss of me", "ok, 'DAD'", "but what of the children?", "?", "workin' on it!", "on it!", "can do, cap'n!", "raseworter pro tip: run it back, but with less 'tude next time.", "who? oh yeah sure thing b0ss", "how about no for a change?", "CAAAAAAAAAAAAAAN DO!", "i'm afraid i can't let you do that.", "i mean like, if you say so, man", "WOOOOOOOOOOOOOOOOOOOOOOOOOOOO", "*nuzzles u*"]
    await ctx.send(random.choice(epicCatchphrases))
    messages = vetoChannel.history(after=twoWeekAgo, limit=None)
    print(messages)
    if messages is None:
        return
    messages = [message async for message in messages]
    acceptedCards:list[str] = []
    errataedCards:list[str] = []
    vetoedCards:list[str] = []
    vetoHell:list[str] = []
    for messageEntry in messages:
        try:
            upvote = get(messageEntry.reactions, emoji=hc_constants.VOTE_UP).count # todo: see if this could be || 0
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

        if get(messageEntry.reactions, emoji = hc_constants.ACCEPT) or get(messageEntry.reactions, emoji = hc_constants.DELETE):
            continue # Skip this card if it has been accepted or deleted. At some point maybe drop the elif here, cause continue skips the rest of the loop
        elif (messageAge < timedelta(days=1)):
            ... # No idea why this case was here... maybe a time buffer

        # Errata needed case
        elif (errata > 4
                and errata >= upvote
                and errata >= downvote):
            errataedCards.append(getCardMessage(messageEntry))
            await messageEntry.add_reaction(hc_constants.ACCEPT)
            thread = messageEntry.guild.get_channel_or_thread(messageEntry.id)
            await thread.edit(archived = True)

        # Accepted case
        elif (upvote > 4
                and upvote >= downvote
                and upvote >= errata):
            
            await messageEntry.add_reaction(hc_constants.ACCEPT)
            thread = messageEntry.guild.get_channel_or_thread(messageEntry.id)
            await thread.edit(archived = True)
            file = await messageEntry.attachments[0].to_file()
            
            acceptanceMessage = messageEntry.content
            # consider putting most of this into acceptCard
            # this is pretty much the same as getCardMessage but teasing out the db logic too was gonna suck
            dbname = ""
            card_author = ""
            if (len(acceptanceMessage)) == 0:
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
            acceptCard(bot=bot,cardMessage=cardMessage,cardName=dbname,authorName=card_author,file=file)

        # Veto case
        elif (downvote > 4 and downvote >= upvote and downvote >= errata):
            vetoedCards.append(getCardMessage(messageEntry))
            await messageEntry.add_reaction(hc_constants.ACCEPT) # see ./README.md

        # Veto Hell
        elif (messageAge > timedelta(days=3)):
            thread = messageEntry.guild.get_channel_or_thread(messageEntry.id)
            role = get(messageEntry.guild.roles, id = hc_constants.VETO_COUNCIL_MAYBE)
            await thread.send(role.mention)
            vetoHell.append(getCardMessage(messageEntry))


    await vetoDiscussionChannel.send(content= f"!! VETO POLLS HAVE BEEN PROCESSED !!")

    # had to use format because python doesn't like \n inside template brackets
    await vetoDiscussionChannel.send(content = "\n\nACCEPTED CARDS: \n{0}".format("\n".join(acceptedCards)))
    await vetoDiscussionChannel.send(content = "\n\nNEEDS ERRATA: \n{0}".format("\n".join(errataedCards)))
    await vetoDiscussionChannel.send(content = "\n\nnVETOED: \n{0}".format("\n".join(vetoedCards)))
    await vetoDiscussionChannel.send(content = "\n\nnVETO HELL: \n{0}".format("\n".join(vetoHell)))


bot.run(DISCORD_ACCESS_TOKEN)

def getCardMessage(acceptanceMessage:str):
    dbname = ""
    card_author = ""
    if (len(acceptanceMessage)) == 0:
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


