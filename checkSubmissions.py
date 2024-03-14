

from datetime import datetime, timezone, timedelta
from acceptCard import acceptCard
import hc_constants
from discord.ext import commands
from discord.utils import get

from is_mork import is_mork, reasonableCard



async def checkSubmissions(bot:commands.Bot):
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
            continue # just ignore these
        upvote = get(messageEntry.reactions, emoji = hc_constants.VOTE_UP)
        downvote = get(messageEntry.reactions, emoji = hc_constants.VOTE_DOWN)
        if upvote and downvote:
            upCount = upvote.count
            downCount = downvote.count
            messageAge = timeNow - messageEntry.created_at
            # card was voted in
        if (upCount - downCount) > 24 and len(messageEntry.attachments) > 0 and messageAge >= timedelta(days=1) and is_mork(messageEntry.author.id):
            if downCount == 1:
                user = await bot.fetch_user(hc_constants.EXALTED_ONE) # If a message would be accepted, but there's only a single downvote, need Exalted to add another downvote
                await user.send("Verify " + messageEntry.jump_url)
                continue
            file = await messageEntry.attachments[0].to_file()
            acceptContent = messageEntry.content + " was accepted"

            mention = f'<@{str(messageEntry.raw_mentions[0])}>'
            accepted_message_no_mentions = messageEntry.content.replace(mention, messageEntry.mentions[0].name)
            if reasonableCard():
                acceptanceMessage = accepted_message_no_mentions
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
                acceptCard(bot=bot,cardMessage=f"✨✨ {cardMessage} ✨✨",cardName=dbname,authorName=card_author,file=file)
            else:
                copy = await messageEntry.attachments[0].to_file()
                await vetoChannel.send(content=accepted_message_no_mentions, file=copy)
            copy2 = await messageEntry.attachments[0].to_file()
            logContent = f"{acceptContent}, message id: {messageEntry.id}, upvotes: {upCount}, downvotes: {downCount}"
            await acceptedChannel.send(content=acceptContent)
            await acceptedChannel.send(content="", file=file)
            await logChannel.send(content=logContent, file=copy2)
            await messageEntry.delete()
            continue
    print("------done checking submissions-----")
