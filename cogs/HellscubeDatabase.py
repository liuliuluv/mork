import random
import discord
from discord.ext import commands
from random import randrange

from datetime import datetime, timezone, timedelta
from cardNameRequest import cardNameRequest
import hc_constants
from sendImage import sendImage


from shared_vars import intents,allCards,cardList

client = discord.Client(intents=intents)



class HellscubeDatabaseCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
    
    # okay not technically a DB command
    @commands.command()
    async def randomReject(self, channel, num=0):
        """
        Returns a random card image from #submissions.
        Chooses a random date between the start of submissions and now, then gets history near that date.
        Chooses a random message from that history. If chosen message has no image, calls itself up to 9 more times.
        """
        if num > 9:
            await channel.send("Sorry, no cards were found.")
            return
        subStart = datetime.strptime('5/13/2021 1:30 PM', '%m/%d/%Y %I:%M %p')
        timeNow = datetime.now(timezone.utc)
        timeNow = timeNow.replace(tzinfo=None)
        delta = timeNow - subStart
        intDelta = (delta.days * 24 * 60 * 60) + delta.seconds
        randomSecond = randrange(intDelta)
        randomDate = subStart + timedelta(seconds=randomSecond)
        subChannel = self.bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
        subHistory = subChannel.history(around = randomDate)
        subHistory = [message async for message in subHistory]
        randomNum = randrange(1, len(subHistory)) - 1
        if len(subHistory[randomNum].attachments) > 0:
            file = await subHistory[randomNum].attachments[0].to_file()
            await channel.send(content = "", file = file)
        else:
            num += 1
            command = self.bot.get_command("randomReject")
            await channel.invoke(command, num)

    @commands.command(name="random")
    async def randomCard(self,channel):
        print(allCards)
        card = allCards[random.choice(list(allCards.keys()))]
        await sendImage(card.getImg(), card.getName(), channel)

    @commands.command()
    async def creator(self, channel, *cardName):
        name = await cardNameRequest(' '.join(cardName).lower())
        await channel.send(allCards[name].getName() + " created by: " + allCards[name].getCreator())
    
    @commands.command()
    async def rulings(self, channel, *cardName):
        name = await cardNameRequest(' '.join(cardName).lower())
        message = "something went wrong!"
        for card in cardList:
            if card.name().lower() == name:
                rulings = card.rulings()
                rulingsList = rulings.split("\\\\\\")
                if (len(rulings) == 0):
                    message = "There are no rulings for " + name
                else:
                    message = f'rulings for {name}:'
                    for i in rulingsList:
                        message = message + "\n```" + i + "```"
        await channel.send(message)

    @commands.command()
    async def info(self, channel, *cardName):
        name = await cardNameRequest(' '.join(cardName).lower())
        message = "something went wrong!"
        for card in cardList:
            if card.name().lower() == name:
                creator = card.creator()
                cardset = card.cardset()
                legality = card.legality()
                rulings = card.rulings()
                rulingsList = rulings.split("\\\\\\")
                message = name + "\ncreator: " + creator + "\nset: " + cardset + "\nlegality: " + legality + "\nrulings: "
                for i in rulingsList:
                    message = message + "\n```" + i + "```"
        await channel.send(message)



    @commands.command()
    async def search(self, ctx:commands.Context, *conditions):
        restrictions = {}
        for i in conditions:
            if i.lower()[0:2] == "o:":
                if "text" in restrictions.keys():
                    restrictions["text"].append(i[2:])
                else:
                    restrictions["text"] = [i[2:]]
            if i.lower()[0:2] == "f:":
                if "flavor" in restrictions.keys():
                    restrictions["flavor"].append(i[2:])
                else:
                    restrictions["flavor"] = [i[2:]]
            if i.lower()[0:2] == "t:":
                if "types" in restrictions.keys():
                    restrictions["types"].append(i[2:])
                else:
                    restrictions["types"] = [i[2:]]
            if i.lower()[0:2] == "n:":
                if "name" in restrictions.keys():
                    restrictions["name"].append(i[2:])
                else:
                    restrictions["name"] = [i[2:]]
            if i.lower()[0:5] == "from:":
                if "creator" in restrictions.keys():
                    restrictions["creator"].append(i[5:])
                else:
                    restrictions["creator"] = [i[5:]]
            if i.lower()[0:2] == "s:":
                if "cardset" in restrictions.keys():
                    restrictions["cardset"].append(i[2:])
                else:
                    restrictions["cardset"] = [i[2:]]
            if i.lower()[0:6] == "legal:":
                if "legality" in restrictions.keys():
                    restrictions["legality"].append(i[6:])
                else:
                    restrictions["legality"] = [i[6:]]
            if i.lower()[0:3] == "cmc":
                if "cmc" in restrictions.keys():
                    restrictions["cmc"].append((i[4:], i[3]))
                else:
                    restrictions["cmc"] = [(i[4:], i[3])]
            if i.lower()[0:3] == "pow":
                if "pow" in restrictions.keys():
                    restrictions["pow"].append((i[4:], i[3]))
                else:
                    restrictions["pow"] = [(i[4:], i[3])]
            if i.lower()[0:3] == "tou":
                if "tou" in restrictions.keys():
                    restrictions["tou"].append((i[4:], i[3]))
                else:
                    restrictions["tou"] = [(i[4:], i[3])]
            if i.lower()[0:3] == "loy":
                if "loy" in restrictions.keys():
                    restrictions["loy"].append((i[4:], i[3]))
                else:
                    restrictions["loy"] = [(i[4:], i[3])]
            if i.lower()[0] == "c" and i.lower()[1] in "<=>":
                if "color" in restrictions.keys():
                    restrictions["color"].append((i[2:], i[1]))
                else:
                    restrictions["color"] = [(i[2:], i[1])]
        print(restrictions)
        if restrictions == {}:
            return
        
        matchingCards = searchFor(restrictions)
        message = printCardNames(matchingCards)
        if message == "":
            message = "Nothing found"
        n=2000
        messages = [message[i:i+n] for i in range(0, len(message), n)]
        for msg in messages:
            await ctx.send(msg)





async def setup(bot:commands.Bot):
    await bot.add_cog(HellscubeDatabaseCog(bot))



def searchFor(searchDict):
  for i in ["types", "text", "flavor", "name", "creator", "cardset", "legality"]:
    if not i in searchDict.keys():
      searchDict[i] = None
  for i in ["cmc", "pow", "tou", "loy", "color"]:
    if not i in searchDict.keys():
      searchDict[i] = [(None, None)]
  hits = []
  for i in cardList:
    if checkForString(searchDict["types"], i.types())\
    and checkForString(searchDict["text"], i.text())\
    and checkForString(searchDict["flavor"], i.flavor())\
    and checkForString(searchDict["name"], i.name())\
    and checkForString(searchDict["creator"], i.creator())\
    and checkForString(searchDict["cardset"], i.cardset())\
    and checkForString(searchDict["legality"], i.legality()):
      if checkForInt(searchDict["cmc"], i.cmc()) and checkForInt(searchDict["tou"], i.toughness()) and checkForInt(searchDict["pow"], i.power()) and checkForInt(searchDict["loy"], i.loyalty()):
        if checkForColor(searchDict["color"], i.colors()):
          hits.append(i)
  return hits


def checkForString(condition, data):
  if type(condition) is str:
    condition = [condition.lower()]
  if condition:
    for j in condition:
      if not j.lower() in data:
        return False
  return True


def checkForInt(condition, data):
  for i in condition:
    if i[0] != None:
      number = int(i[0])
      opperator = i[1]
      if opperator == "=":
        if not number in data:
          return False
      if opperator == ">":
        works = False
        for j in data:
          if j > number:
            works = True
        if not works:
          return False
      if opperator == "<":
        works = False
        for j in data:
          if j < number:
            works = True
        if not works:
          return False
  return True


colorLetterDict = {
  "w" : "white",
  "u" : "blue",
  "b" : "black",
  "r" : "red",
  "g" : "green",
  "p" : "purple",
  "m" : "multicolor",
}

def checkForColor(condition, data):
  if not condition[0][0]:
    return True
  allowed = True
  for requirement in condition:
    allowedColors = [""]
    requiredColors = []
    if requirement[1] == "=":
      for i in requirement[0]:
        if i in colorLetterDict.keys():
          requiredColors.append(colorLetterDict[i])
          allowedColors.append(colorLetterDict[i])
    if requirement[1] == ">":
      for i in requirement[0]:
        if i in colorLetterDict.keys():
          requiredColors.append(colorLetterDict[i])
      for i in colorLetterDict.keys():
        allowedColors.append(colorLetterDict[i])
    if requirement[1] == "<":
      for i in requirement[0]:
        if i in colorLetterDict.keys():
          allowedColors.append(colorLetterDict[i])
    for i in requiredColors:
      if i == "multicolor":
        if len(data) < 2:
          allowed = False
      else:
        if not i in data:
          allowed = False
    for i in data:
      if not "m" in requirement[0]:
        if not i in allowedColors:
          allowed = False
  return allowed


def printCardNames(cards):
  returnString = "Results: "
  returnString += str(len(cards)) + "\n"
  for i in cards:
    returnString += i.name() + "\n"
  return returnString


