from Mork import MyBot
import hc_constants
from datetime import datetime, timezone, timedelta
from discord.utils import get

async def checkErrataSubmissions(bot:MyBot):
  subChannel = bot.get_channel(hc_constants.FOUR_ZERO_ERRATA_SUBMISSIONS_CHANNEL)
  acceptedChannel = bot.get_channel(hc_constants.FOUR_ZERO_ERRATA_ACCEPTED_CHANNEL)
  timeNow = datetime.now(timezone.utc)
  oneWeek = timeNow + timedelta(weeks=-1)
  messages = subChannel.history(after=oneWeek, limit=None)
  if messages is None:
    return
  messages = [message async for message in messages]
  for i in range(len(messages)):
    if "@everyone" in messages[i].content:
      continue
    if get(messages[i].reactions, emoji=hc_constants.ACCEPT):
      continue
    upvote = get(messages[i].reactions, emoji=hc_constants.VOTE_UP)
    downvote = get(messages[i].reactions, emoji=hc_constants.VOTE_DOWN)

    if upvote and downvote:
      upCount = upvote.count
      downCount = downvote.count
      messageAge = timeNow - messages[i].created_at
      if (upCount - downCount) > 14 and messageAge >= timedelta(days=1):
        acceptContent = messages[i].content
        await acceptedChannel.send(content=acceptContent)
        await messages[i].add_reaction(hc_constants.ACCEPT)
  print("------done checking errata submissions-----")
