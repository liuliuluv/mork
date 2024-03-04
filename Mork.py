import io
import aiohttp
import discord
import asyncio
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint as pp
from discord.utils import get
from discord import Embed
from dpymenus import PaginatedMenu
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
from random import randrange

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from login_with_service_account import login_with_service_account
from secrets.discord_token import DISCORD_ACCESS_TOKEN


import hc_constants

gauth = login_with_service_account()
drive = GoogleDrive(gauth)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.guilds = True


class MyBot(commands.Bot):
    async def setup_hook(self):
        print('This is asynchronous!')
        initialExtensions = [
          'cogs.SpecificCards',
          'cogs.Messages',
          'cogs.Roles',
          'cogs.Lifecycle'
          ]
        for i in initialExtensions:
            await self.load_extension(i)

bot = MyBot(command_prefix='!', case_insensitive=True, intents=intents)
bot.remove_command('help')


@bot.command()
async def check_cogs(ctx, cog_name):
    try:
        await bot.load_extension(f"cogs.{cog_name}")
    except commands.ExtensionAlreadyLoaded:
        await ctx.send("Cog is loaded")
    except commands.ExtensionNotFound:
        await ctx.send("Cog not found")
    else:
        await ctx.send("Cog is unloaded")
        await bot.unload_extension(f"cogs.{cog_name}")

client = discord.Client(intents=intents)


scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("secrets/client_secrets.json", scope)

googleClient = gspread.authorize(creds)

cardSheet = googleClient.open_by_key(hc_constants.HELLSCUBE_DATABASE).get_worksheet(0)
cardSheetUnapproved = googleClient.open_by_key(hc_constants.HELLSCUBE_DATABASE).get_worksheet(1)
print(cardSheet)
allCards = {}

bannedUserIds = []

statusList = ["Haha Gottem in 2020", "Hugh Man in EDH", "the funny dreadmaw card", "Hellscube Victory in Competative", "with old companion rules", "Obama tribal EDH", "irefeT tribal", "Temple of @creator", "cheat big shit out", "v1.0", "2/3 Corpse Knight", "Forbiddenest Ritual for value", "71 lands and Haha Gottem", "PICKLE K'RRIK!", "\"colorless\" card draw", "HellsEdh", "hellscube", "Hellscube Jumpstart", "comboless Zero with Nothing", "with MaRo's feelings", "with Exalted's sanity", "Slot Filler for draw cards equal to 2 minus one", "Epicnessbrian tribal", "a minigame", "a subgame", "a supergame", "The First Pick", "Tendrils of Shahrazad", "hide and seek with Liu Bei's wallet", "with slots", "Redundant Acceleration for 1 card", "with !podcast", "with #brainstorming-shitposts", "with no banlist", "Hatebear With Useful Abilities", "JacobsRedditUsername Tribal", "white card draw!!1!?1!??!?", "Force of Bill for 5 mana", "with bears. So... many... bears...", "Epic Games", "6-mana 1/1s", "a full playset of worm", "all of the murder but _ cycle", "with the idea of skipping to 3.0", "1 cmc super friends", "all the creator lands", "strip hellscube vintage", "cooldownguy vintage", "6-color goodstuff", "a 41 card draft deck", "infinite basics in the sideboard", "10.000 Islands in the main", "#avatar in discord", "Avatar of Discord, Please spam Attack. Please", "Avatar of Discord, Please spam Defence. Please", "Avatar of Discord, Please spam Evasion. Please", "Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing...", "blue bears"]



authorSplit = "$#$#$"
quoteSplit = ";%;%;"
global blueRed
blueRed = False

class Card:
  def __init__(self, name, img, creator):
    self._name = name
    self._img = img
    self._creator = creator
  def getName(self):
    return self._name
  def getImg(self):
    return self._img
  def getCreator(self):
    return self._creator

cardSheetSearch = googleClient.open("Hellscube Database").worksheet("Database Bot Read")

KissSheet = googleClient.open("Hellscube Database").worksheet("Zaxer's Wacky Database Sheet")


cardsDataSearch = cardSheetSearch.col_values(2)

cardList=[]

class Side:
  def __init__(self, cost, supertypes, types, subtypes, power, toughness, loyalty, text, flavor):
    self._cost = cost
    self._supertypes = supertypes
    self._types = types
    self._subtypes = subtypes
    self._power = power
    self._toughness = toughness
    self._loyalty = loyalty
    self._text = text
    self._flavor = flavor
  def cost(self):
    return self._cost
  def types(self):
    return self._supertypes + self._types + self._subtypes
  def power(self):
    return self._power
  def toughness(self):
    return self._toughness
  def loyalty(self):
    return self._loyalty
  def text(self):
    return self._text
  def flavor(self):
    return self._flavor

class cardSearch:
  def __init__(self, name, img, creator, cmc, colors, sides, cardset, legality, rulings):
    self._name = name
    self._img = img
    self._creator = creator
    self._cmc = cmc
    self._colors = colors
    self._sides = sides
    self._cardset = cardset
    self._legality = legality
    self._rulings = rulings
  def name(self):
    return self._name
  def img(self):
    return self._img
  def creator(self):
    return self._creator
  def legality(self):
      return self._legality
  def rulings(self):
      return self._rulings
  def cmc(self):
    return [self._cmc]
  def colors(self):
    return self._colors
  def cardset(self):
    return self._cardset
  def sides(self):
      return self._sides
  def types(self):
    returnList = []
    for i in self._sides:
      returnList += i.types()
    return list(set(returnList))
  def power(self):
    returnList = []
    for i in self._sides:
      returnList.append(i.power())
    return list(set(returnList))
  def toughness(self):
    returnList = []
    for i in self._sides:
      returnList.append(i.toughness())
    return list(set(returnList))
  def loyalty(self):
    returnList = []
    for i in self._sides:
      returnList.append(i.loyalty())
    return list(set(returnList))
  def text(self):
    returnString = ""
    for i in self._sides:
      returnString += i.text()
    return returnString
  def flavor(self):
    returnString = ""
    for i in self._sides:
      returnString += i.flavor()
    return returnString

def genSide(stats):
  cost = stats[0]
  if stats[1] != "":
    supertypes = stats[1].split(";")
  else:
    supertypes = []
  types = stats[2].split(";")
  if stats[3] != "":
    subtypes = stats[3].split(";")
  else:
    subtypes = []
  power = 0
  toughness = 0
  loyalty = 0
  if stats[4] != "" and stats[4] != " ":
    power = int(stats[4])
  if stats[5] != "" and stats[5] != " ":
    toughness = int(stats[5])
  if stats[6] != "" and stats[6] != " ":
    loyalty = int(stats[6])
  text = stats[7]
  flavor = stats[8]
  return Side(cost, supertypes, types, subtypes, power, toughness, loyalty, text, flavor)

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

for i in cardsDataSearch:
  try:
    if i == "%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%%&%&%":
      break
    stats = i.lower().split("%&%&%")
    name = stats[0]
    img = stats[1]
    creator = stats[2]
    cmc = 0
    cardset = stats[3]
    legality = stats[4]
    rulings = stats[5]
    if stats[6] != "" and stats[6] != " ":
      cmc = int(stats[6])
    if stats[7] == "colorless":
      stats[7] = ""
    colors = stats[7].split(";")
    sides = []
    sides.append(genSide(stats[8:]))
    if stats[20] != "" and stats[20] != " ":
      sides.append(genSide(stats[18:]))
    if stats[29] != "" and stats[29] != " ":
      sides.append(genSide(stats[27:]))
    if stats[38] != "" and stats[38] != " ":
      sides.append(genSide(stats[36:]))
    cardList.append(cardSearch(name, img, creator, cmc, colors, sides, cardset, legality, rulings))
  except:
    print(i)
    print(i.lower().split("%&%&%"))

def printCardNames(cards):
  returnString = "Results: "
  returnString += str(len(cards)) + "\n"
  for i in cards:
    returnString += i.name() + "\n"
  return returnString

@bot.command()
async def search(ctx, *conditions):
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
  message = printCardNames(searchFor(restrictions))
  if message == "":
    message = "Nothing found"
  n=2000
  messages = [message[i:i+n] for i in range(0, len(message), n)]
  for msg in messages:
    await ctx.send(msg)



async def sendImage(url, cardname, channel):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      if resp.status != 200:
        await channel.send('Something went wrong while getting the link for ' + cardname + '. Wait for @exalted to fix it.')
        return
      data = io.BytesIO(await resp.read())
      await channel.send(file=discord.File(data, url))

async def sendImageReply(url, cardname, message):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      if resp.status != 200:
        await message.reply('Something went wrong while getting the link for ' + cardname + '. Wait for @exalted to fix it.')
        return
      data = io.BytesIO(await resp.read())
      sentMessage = await message.reply(file=discord.File(data, url), mention_author=False)
      await sentMessage.add_reaction("❌")

async def similarity(name, key):
  weight = 0
  for i in range(len(key)):
    for j in range(len(name)):
      for x in range(1, min( len(name) - j , len(key) - i ) + 1):
        if key[i:i+x] != name[j:j+x] or x == min( len(name) - j , len(key) - i ):
          weight += max((x-1) * (x-1) -1, 0)
          break
  if name == key or name + " " == key:
    weight = 10000000
  return weight

async def cardNameRequest(requestName):
  maxWeight = 1
  maxWeightName = ""
  for cardName in allCards.keys():
    currentWeight = await similarity(cardName, requestName)
    if currentWeight > maxWeight:
      maxWeight = currentWeight
      maxWeightName = cardName
    elif currentWeight == maxWeight:
      if len(cardName) < len(maxWeightName):
        maxWeightName = cardName
  return maxWeightName


async def printCardImages(message):
  messageText = message.content.lower().split("{{")[1:]
  for i in range(len(messageText)):
    messageText[i] = messageText[i].split("}}")[0]
  requestedCards = []
  if len(messageText) > 10 and message.author.id != hc_constants.CIRION:
    await message.reply("Don't call more than 10 cards per message, final warning, keep trying and you get blacklisted from the bot. Blame dRafter for this if you're actually trying to use the bot.")
    return
  for cardName in messageText:
    requestedCards.append(await cardNameRequest(cardName))
  for post in requestedCards:
    if post == "":
      await message.reply("No Match Found!", mention_author=False)
    else:
      await sendImageReply(allCards[post].getImg(), allCards[post].getName(), message)

async def addToDrive(message, user, fileID):
  text = ";%;%;"
  text += message
  text += authorSplit
  text += user
  file = drive.CreateFile({'id':fileID})
  update = file.GetContentString() + text
  file.SetContentString(update)
  file.Upload()

@bot.command()
async def quote(ctx, lookback=1):
  if lookback == 0:
    await ctx.send("^\nfucker")
    return
  if lookback>100:
    await ctx.send("Can't look back more than 100 messages")
    return
  messages = ctx.history(limit=lookback+1)
  messages = [message async for message in messages]
  message = messages[lookback]
  if "@" in message.content:
    await ctx.send("You think you're fucking funny, bitch\n\nOh, I'll try to quote a ping it'll be funny and totally not annoying at all.\nYou're a bitch. You suck. Fuck you\n\nYou useless piece of shit. You absolute waste of space and air. You uneducated, ignorant, idiotic dumb swine, you’re an absolute embarrassment to humanity and all life as a whole. The magnitude of your failure just now is so indescribably massive that one hundred years into the future your name will be used as moniker of evil for heretics. Even if all of humanity put together their collective intelligence there is no conceivable way they could have thought up a way to fuck up on the unimaginable scale you just did. When Jesus died for our sins, he must not have seen the sacrilegious act we just witnessed you performing, because if he did he would have forsaken humanity long ago so that your birth may have never become reality. After you die, your skeleton will be displayed in a museum after being scientifically researched so that all future generations may learn not to generate your bone structure, because every tiny detail anyone may have in common with you degrades them to a useless piece of trash and a burden to society.")
    return
  user = message.author.name
  if message.author.id == hc_constants.TIME_SPIRAL and ctx.channel.id != hc_constants.CUBE_CHANNEL:
    await ctx.send("The bot can't quote itself")
    return
  fileID = getFileForChannelId(ctx.channel.id)

  await addToDrive(message.content, user, fileID)
  await ctx.send("\"" + message.content + "\"\n-" + user)

@bot.command()
async def randomquote(ctx, *user):
  fileID = getFileForChannelId(ctx.channel.id)
  file = drive.CreateFile({'id':fileID})
  quoteList = file.GetContentString().split(quoteSplit)
  for i in range(len(quoteList)):
    quoteList[i] = quoteList[i].split(authorSplit)
  if user:
    user = " ".join(user)
    tempList=[]
    for i in quoteList:
      if i[1].lower() == user.lower():
        tempList.append(i)
    quoteList=tempList
    if quoteList == []:
      await ctx.send("No quotes by " + user + " found. :(")
      return
  quote = random.choice(quoteList)
  message = quote[0]
  user = quote[1]
  await ctx.send("\"" + message.replace("\\n", "\n") + "\"\n-" + user)


async def createQuoteMenu(ctx, quoteList):

  pageList = []
  for i in quoteList:
    page = Embed(title=i[1], description=i[0])
    pageList.append(page)

  menu = (PaginatedMenu(ctx)
         .set_timeout(100)
         .add_pages(pageList)
         .show_skip_buttons()
         .hide_cancel_button()
         .persist_on_close()
         .show_page_numbers()
         .show_command_message()
         )
  await menu.open()

@bot.command()
async def randomReject(channel, num=0):
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
  subChannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
  subHistory = subChannel.history(around = randomDate)
  subHistory = [message async for message in subHistory]
  randomNum = randrange(1, len(subHistory)) - 1
  if len(subHistory[randomNum].attachments) > 0:
    file = await subHistory[randomNum].attachments[0].to_file()
    await channel.send(content = "", file = file)
  else:
    num += 1
    command = bot.get_command("randomReject")
    await channel.invoke(command, num)

@bot.command(name="random")
async def randomCard(channel):
  card = allCards[random.choice(list(allCards.keys()))]
  await sendImage(card.getImg(), card.getName(), channel)


def getFileForChannelId(channelId):
  # nsfw file else sfw one ??????
  return "1RNw6b4wUck3HIw1kF7ewmtXE6gSmXSKt" if channelId == hc_constants.UNKNOWN_CHANNEL else "1EdaLJl9Rs0RuigiivckOM1obPmQ99hMg"


@bot.command()
async def searchquote(ctx, text, *user):
  fileID = getFileForChannelId(ctx.channel.id)
  file = drive.CreateFile({'id':fileID})
  quoteList = file.GetContentString().split(quoteSplit)
  for i in range(len(quoteList)):
    quoteList[i] = quoteList[i].split(authorSplit)
  if user:
    user = " ".join(user)
    tempList=[]
    for i in quoteList:
      if i[1].lower() == user.lower():
        tempList.append(i)
    quoteList=tempList
    if quoteList == []:
      await ctx.send("No quotes by " + user + " found. :(")
      return
  tempList=[]
  for i in quoteList:
    if text.lower() in i[0].lower():
      tempList.append(i)
  quoteList=tempList
  if quoteList == []:
    await ctx.send("No quotes with the text " + text + " found. :(")
    return
  if len(quoteList) > 50:
    await ctx.send(str(len(quoteList)) + " quotes found, that's too many, be more specific please")
    return
  elif len(quoteList) > 2:
    await createQuoteMenu(ctx, quoteList)
  else:
    message = ""
    for i in quoteList:
      message += "\"" + i[0].replace("\\n", "\n") + "\"\n-" + i[1] + "\n\n"
    await ctx.send(message)

async def checkSubmissions():
  subChannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
  vetoChannel = bot.get_channel(hc_constants.VETO_CHANNEL)
  acceptedChannel = bot.get_channel(hc_constants.SUBMISSIONS_DISCUSSION_CHANNEL)
  logChannel = bot.get_channel(hc_constants.MORK_SUBMISSIONS_LOGGING_CHANNEL)
  timeNow = datetime.now(timezone.utc)
##  timeNow = timeNow.replace(tzinfo=None)
  oneWeek = timeNow + timedelta(weeks=-1)
  messages = subChannel.history(after=oneWeek, limit=None)
  if messages is None:
    return
  messages = [message async for message in messages]
  for i in range(len(messages)):
    if "@everyone" in messages[i].content:
      continue
    upvote = get(messages[i].reactions, emoji="👍")
    downvote = get(messages[i].reactions, emoji="👎")
    messageAge = timeNow - messages[i].created_at
    if upvote and downvote:
      upCount = upvote.count
      downCount = downvote.count
      #if (upvote.count - downvote.count) < -10 and len(messages[i].attachments) > 0 and messageAge >= timedelta(days=1):
      #  await messages[i].delete()
      if (upCount - downCount) > 24 and len(messages[i].attachments) > 0 and messageAge >= timedelta(days=1) and messages[i].author.id == hc_constants.MORK:
        if downCount == 1:
          user = await bot.fetch_user(hc_constants.EXALTED_ONE)
          await user.send("Verify " + messages[i].jump_url)
          continue
        file = await messages[i].attachments[0].to_file()
        copy = await messages[i].attachments[0].to_file()
        copy2 = await messages[i].attachments[0].to_file()
        acceptContent = messages[i].content + " was accepted "
        mention = f'<@{str(messages[i].raw_mentions[0])}>'
        nickMention = f'<@{str(messages[i].raw_mentions[0])}>'
        removeMention = messages[i].content.replace(mention, "")
        removeMention = removeMention.replace(nickMention, "")
        vetoContent = removeMention + messages[i].mentions[0].name
        logContent = acceptContent + ", message id: " + str(messages[i].id) + ", upvotes: " + str(upCount) + ", downvotes: " + str(downCount)
        await acceptedChannel.send(content=acceptContent)
        await acceptedChannel.send(content="", file=file)
        await vetoChannel.send(content=vetoContent, file=copy)
        await logChannel.send(content=logContent, file=copy2)
        await messages[i].delete()
        continue
      if (upCount - downCount) > 24 and len(messages[i].attachments) > 0 and messageAge >= timedelta(days=1):
        if downCount == 1:
          user = await bot.fetch_user(hc_constants.EXALTED_ONE)
          await user.send("Verify " + messages[i].jump_url)
          continue
        file = await messages[i].attachments[0].to_file()
        copy = await messages[i].attachments[0].to_file()
        copy2 = await messages[i].attachments[0].to_file()
        acceptContent = messages[i].content + " was accepted " + messages[i].author.mention
        vetoContent = messages[i].content + " by " + messages[i].author.name
        logContent = acceptContent + ", message id: " + str(messages[i].id) + ", upvotes: " + str(upCount) + ", downvotes: " + str(downCount)
        await acceptedChannel.send(content=acceptContent)
        await acceptedChannel.send(content="", file=file)
        await vetoChannel.send(content=vetoContent, file=copy)
        await logChannel.send(content=logContent, file=copy2)
        await messages[i].delete()
  print("------done checking submissions-----")

async def checkErrataSubmissions():
  subChannel = bot.get_channel(hc_constants.FOUR_ZERO_ERRATA_SUBMISSIONS_CHANNEL)
  acceptedChannel = bot.get_channel(hc_constants.FOUR_ZERO_ERRATA_ACCEPTED_CHANNEL)
  timeNow = datetime.now(timezone.utc)
##  timeNow = timeNow.replace(tzinfo=None)
  oneWeek = timeNow + timedelta(weeks=-1)
  messages = subChannel.history(after=oneWeek, limit=None)
  if messages is None:
    return
  messages = [message async for message in messages]
  for i in range(len(messages)):
    if "@everyone" in messages[i].content:
      continue
    if get(messages[i].reactions, emoji="✅"):
      continue
    upvote = get(messages[i].reactions, emoji="👍")
    downvote = get(messages[i].reactions, emoji="👎")
    messageAge = timeNow - messages[i].created_at
    if upvote and downvote:
      upCount = upvote.count
      downCount = downvote.count
      if (upCount - downCount) > 14 and messageAge >= timedelta(days=1):
        acceptContent = messages[i].content
        await acceptedChannel.send(content=acceptContent)
        await messages[i].add_reaction("✅")
  print("------done checking errata submissions-----")

# @bot.command()
# async def checkSubTest(ctx):
#  subChannel = bot.get_channel(1005628044075090041)
#  vetoChannel = bot.get_channel(1005628663968059492)
#  acceptedChannel = bot.get_channel(1005628663968059492)
#  logChannel = bot.get_channel(hc_constants.MORK_SUBMISSIONS_LOGGING_CHANNEL)
#  timeNow = datetime.now(timezone.utc)
#  timeNow = timeNow.replace(tzinfo=None)
#  oneWeek = timeNow + timedelta(weeks=-1)
#  messages = subChannel.history(after=oneWeek, limit=None)
#  if messages is None:
#    return
#  messages = await messages.flatten()
#  for i in range(len(messages)):
#      upvote = get(messages[i].reactions, emoji="👍")
#      downvote = get(messages[i].reactions, emoji="👎")
#      if len(messages[i].attachments) > 0 and messages[i].author.id == hc_constants.MORK:
#        file = await messages[i].attachments[0].to_file()
#        copy = await messages[i].attachments[0].to_file()
#        copy2 = await messages[i].attachments[0].to_file()
#        acceptContent = messages[i].content + " was accepted "
#        mention = "<@" + str(messages[i].raw_mentions[0]) + ">"
#        nickMention = "<@!" + str(messages[i].raw_mentions[0]) + ">"
#        removeMention = messages[i].content.replace(mention, "")
#        removeMention = removeMention.replace(nickMention, "")
#        vetoContent = removeMention + messages[i].mentions[0].name
#        logContent = acceptContent + ", message id: " + str(messages[i].id) + ", upvotes: " + str(upvote.count) + ", downvotes: " + str(downvote.count)
#        await acceptedChannel.send(content=acceptContent)
#        await acceptedChannel.send(content="", file=file)
#        await vetoChannel.send(content=vetoContent, file=copy)
#        await logChannel.send(content=logContent, file=copy2)
#        await messages[i].delete()

# @tasks.loop(hours=4, count=2)
# async def my_task():
#   print("doing task")
#   if my_task.current_loop != 0:
#     subchannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
#     message = await subchannel.fetch_message(1091591370956865577)
#     mork = bot.get_user(538770459517255711)
#     file = await message.attachments[0].to_file()
#     sentMessage = await subchannel.send(content=message.content + " by " + mork.mention, file=file)
#     await sentMessage.add_reaction("👍")
#     await sentMessage.add_reaction("👎")
#     await sentMessage.add_reaction("❌")

##@bot.command()
##async def morkPost(ctx, messageID):
##   message = await ctx.fetch_message(messageID)
##   subchannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
##   mork = bot.get_user(hc_constants.MORK)
##   file = await message.attachments[0].to_file()
##   sentMessage = await subchannel.send(content=message.content + " by " + mork.mention, file=file)
##   await sentMessage.add_reaction("👍")
##   await sentMessage.add_reaction("👎")
##   await sentMessage.add_reaction("❌")

log = ""

@bot.command(name="dumplog")
async def _dumplog(ctx):
    global log
    if ctx.author.id == hc_constants.EXALTED_ONE:
        with open("log.txt", 'a', encoding='utf8') as file:
            file.write(log)
            log = ""
            print("log dumped")

@bot.command()
async def getMessage(ctx, id):
  subChannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
  message = await subChannel.fetch_message(id)
  await ctx.send(message.jump_url)


@bot.event
async def on_ready():

  global log
  print(f'{bot.user.name} has connected to Discord!')
  # debug 
  return 

  nameList = cardSheet.col_values(1)[3:]
  imgList = cardSheet.col_values(2)[3:]
  creatorList = cardSheet.col_values(3)[3:]

  for i in range(len(nameList)):
    allCards[nameList[i].lower()] = Card(nameList[i], imgList[i], creatorList[i])
  bot.loop.create_task(status_task())
  while True:
    await asyncio.sleep(3600)
    with open("log.txt", 'a', encoding='utf8') as file:
      file.write(log)
      log = ""

async def status_task():
  # debug
  print('status_task loop')
  return
  while True:
    creator = random.choice(cardSheet.col_values(3)[4:])
    action = random.choice(statusList)
    status = action.replace("@creator", creator)
    print(status)
    await checkSubmissions()
    await checkErrataSubmissions()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(status))
    await asyncio.sleep(300)

@bot.command()
async def macro(ctx, thing, *args):
  if thing == "help":
    message = "Macros are:\nJoke [word]\n"
    for name in hc_constants.macroList.keys():
      if type(hc_constants.macroList[name]) is str:
        message += name
        message += "\n"
      else:
        message += name
        message += "\n"
        for subname in hc_constants.macroList[name]:
          message += f"    {subname}\n"
    await ctx.send(message)
    return
  if ctx.channel.id == hc_constants.UNKNOWN_CHANNEL:
    if thing.lower() in hc_constants.macroNsfwList.keys():
      if type(hc_constants.macroNsfwList[thing.lower()]) is str:
        await ctx.send(hc_constants.macroNsfwList[thing.lower()].replace("@arg", " ".join(args)))
      else:
        await ctx.send(hc_constants.macroNsfwList[thing.lower()][args[0].lower()])
      return
  if thing.lower() in hc_constants.macroList.keys():
    if type(hc_constants.macroList[thing.lower()]) is str:
      await ctx.send(hc_constants.macroList[thing.lower()].replace("@arg", " ".join(args)))
    else:
      pp.pprint(hc_constants.macroList[thing.lower()])
      await ctx.send(hc_constants.macroList[thing.lower()][args[0].lower()])

@bot.command()
async def creator(channel, *cardName):
  name = await cardNameRequest(' '.join(cardName).lower())
  await channel.send(allCards[name].getName() + " created by: " + allCards[name].getCreator())

@bot.command()
async def info(channel, *cardName):
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

@bot.command()
async def rulings(channel, *cardName):
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

@bot.command()
async def gameNight(ctx, mode, game):
  #create, remove, get, lose, tag, list
  if mode == "create":
    file = drive.CreateFile({'id':hc_constants.GAME_FILE_ID})
    output = file.GetContentString()
    if not game.lower() in output.replace('\r','').split("\n"):
      output = output + game.lower() + "\n"
      file.SetContentString(output)
      file.Upload()
      await ctx.send("Created game \"" + game.lower() + "\"")
    else:
      await ctx.send("This game already exist.")
  if mode == "list":
    output = drive.CreateFile({'id':hc_constants.GAME_FILE_ID}).GetContentString()
    await ctx.send(output)
  if mode == "amount":
    games = drive.CreateFile({'id':hc_constants.GAME_FILE_ID}).GetContentString().replace('\r','').split("\n")
    amount = []
    users = drive.CreateFile({'id':hc_constants.USER_GAME_FILE_ID}).GetContentString().replace('\r','').split("\n")
    for x in range(len(games)):
      amount.append(0)
      for i in users:
        if "$%$%$" in i:
          if i.split("$%$%$")[1] == games[x].lower():
            amount[x] += 1
    result = "Amount of users per game:\n"
    for i in range(len(amount)):
      result += games[i]
      result += ": "
      result += str(amount[i])
      result += "\n"
    await ctx.send(result)
  if mode == "remove":
    role = get(ctx.message.author.guild.roles, id=int(631288945044357141))
    if role in ctx.author.roles:
      file1 = drive.CreateFile({'id':hc_constants.GAME_FILE_ID})
      gnRoles = file1.GetContentString()
      if game.lower() in gnRoles.replace('\r','').split("\n"):
        file2 = drive.CreateFile({'id':hc_constants.USER_GAME_FILE_ID})
        gnPeople = file2.GetContentString()
        options = gnPeople.replace('\r','').split("\n")
        for i in options:
          if "$%$%$" in i:
            if i.split("$%$%$")[1] == game.lower():
              options.remove(i)
        update = "\n".join(options)
        file2.SetContentString(update)
        file2.Upload()
        await ctx.send("Removed role \"" + game.lower() + "\" from everyone")
        options = gnRoles.replace('\r','').split("\n")
        for i in options:
          if i == game.lower():
            options.remove(i)
        update = "\n".join(options)
        file1.SetContentString(update)
        file1.Upload()
        await ctx.send("Removed role \"" + game.lower() + "\" from existence")
      else:
        await ctx.send("This game doesn't exist.")
    else:
      await ctx.send("Removing games is only available to mods, probably tag one of them if you need the game removed.")
  if mode == "get":
    if game.lower() in drive.CreateFile({'id':hc_constants.GAME_FILE_ID}).GetContentString().replace('\r','').split("\n"):
      file = drive.CreateFile({'id':hc_constants.USER_GAME_FILE_ID})
      gnPeople = file.GetContentString()
      gnPeople = gnPeople + (str(ctx.author.id)) + "$%$%$" + game.lower() + "\n"
      file.SetContentString(gnPeople)
      file.Upload()
      await ctx.send("Gave you game role for game \"" + game.lower() + "\"")
    else:
      await ctx.send("This game doesn't exist.")
  if mode == "lose":
    if game.lower() in drive.CreateFile({'id':hc_constants.GAME_FILE_ID}).GetContentString().replace('\r','').split("\n"):
      file = drive.CreateFile({'id':hc_constants.USER_GAME_FILE_ID})
      gnPeople = file.GetContentString()
      options = gnPeople.replace('\r','').split("\n")
      for i in options:
        if "$%$%$" in i:
          if i.split("$%$%$")[1] == game.lower() and int(i.split("$%$%$")[0]) == ctx.author.id:
            options.remove(i)
            update = "\n".join(options)
            file.SetContentString(update)
            file.Upload()
            await ctx.send("Removed role \"" + game.lower() + "\" from you")
    else:
      await ctx.send("This game doesn't exist.")
  if mode == "tag":
    if game.lower() in drive.CreateFile({'id':hc_constants.GAME_FILE_ID}).GetContentString().replace('\r','').split("\n"):
      options = drive.CreateFile({'id':hc_constants.USER_GAME_FILE_ID}).GetContentString().replace('\r','').split("\n")
      userIds = []
      for i in options:
        if "$%$%$" in i:
          if i.split("$%$%$")[1] == game.lower():
            userIds.append(i.split("$%$%$")[0])
      result = "Wanna play a game of " + game.lower() + "\n"
      for i in userIds:
        result += "<@" + i + ">\n"
      await ctx.send(result)
    else:
      await ctx.send("This game doesn't exist.")
  if mode == "who":
    if game.lower() in drive.CreateFile({'id':hc_constants.GAME_FILE_ID}).GetContentString().replace('\r','').split("\n"):
      options = drive.CreateFile({'id':hc_constants.USER_GAME_FILE_ID}).GetContentString().replace('\r','').split("\n")
      userIds = []
      for i in options:
        if "$%$%$" in i:
          if i.split("$%$%$")[1] == game.lower():
            userIds.append(i.split("$%$%$")[0])
      result = "All people who play " + game.lower() + " are:\n"
      for i in userIds:
        try:
          g = await bot.fetch_user(i)
          result += g.name + "\n"
        except:
          ...
      await ctx.send(result)
    else:
      await ctx.send("This game doesn't exist.")
  if mode == "search":
    options = drive.CreateFile({'id':hc_constants.USER_GAME_FILE_ID}).GetContentString().replace('\r','').split("\n")
    userGames = []
    for i in options:
      if "$%$%$" in i:
        try:
          user = await bot.fetch_user(int(i.split("$%$%$")[0]))
          print(game.lower(), user.name)
          if game.lower() in user.name.lower():
            userGames.append(i.split("$%$%$")[1])
        except:
          ...
    result = "User " + game.lower() + " has roles for the following games\n"
    for i in userGames:
      result += i + "\n"
    if len(userGames) > 0:
      await ctx.send(result)
    else:
      await ctx.send("User has no game roles")

#for card-brazil and card-netherlands
@bot.command()
async def goodbye(ctx):
  if ctx.channel.id == hc_constants.MAYBE_BRAZIL_CHANNEL or ctx.channel.id == hc_constants.MAYBE_ONE_WORD_CHANNEL:
    messages = ctx.channel.history(limit=500)
    messages = [message async for message in messages]
    card = ""
    for i in range(1, len(messages)):
      if messages[i].content.lower().startswith("start"):
        break
      if messages[i].content != "":
        if messages[i].content[0] != "(":
          card = messages[i].content + " " + card
    card = card.replace("/n", "\n")
    cubeChannel = bot.get_channel(hc_constants.CUBE_CHANNEL)
    await cubeChannel.send(card)
    await ctx.channel.send(card)

@bot.command()
async def BlueRed(ctx):
  if ctx.author.id == hc_constants.CIRION:
    global BlueRed
    if BlueRed:
      BlueRed = False
      await ctx.send("Turned Off")
    else:
      BlueRed = True
      await ctx.send("Turned On")
  else:
    await ctx.send("cirion Only Command")

@bot.command()
async def menu(ctx):
  if ctx.channel.id == hc_constants.RESOURCES_CHANNEL or 654835483771273218:
    embed = discord.Embed(title="Resources Menu", description="[Channel Explanation](https://discord.com/channels/631288872814247966/803384271766683668/803384426360078336)\n[Command List](https://discord.com/channels/631288872814247966/803384271766683668/803389199503982632)\n[Achievements](https://discord.com/channels/631288872814247966/803384271766683668/803389622247882782)\n[Database](https://discord.com/channels/631288872814247966/803384271766683668/803390530145878057)\n[Release Notes](https://discord.com/channels/631288872814247966/803384271766683668/803390718801346610)\n[Cubecobras](https://discord.com/channels/631288872814247966/803384271766683668/803391239294025748)\n[Tabletop Simulator](https://discord.com/channels/631288872814247966/803384271766683668/803391314095636490)")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
  await ctx.send("https://discord.com/channels/631288872814247966/803384271766683668/803389199503982632")
"""
@bot.command()
async def createtable(ctx):
  if ctx.author.id == hc_constants.EXALTED_ONE:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE [IF NOT EXISTS] POPCORN
      (CHANNEL TEXT PRIMARY KEY  NOT NULL,
      CARDTEXT TEXT);''')
    print("popcorn table created")
    cur.execute("INSERT INTO POPCORN(CHANNEL,CARDTEXT) VALUES ('Bot Test','')")
    print("data inserted")
    conn.commit()
    conn.close()
    ctx.channel.send("finished")
"""

@bot.event
async def on_raw_reaction_add(reaction):
  # debug
  return
  if str(reaction.emoji) == "❌" and reaction.user_id != hc_constants.MORK:
    guild = bot.get_guild(reaction.guild_id)
    channel = guild.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    if reaction.member in message.mentions and message.author.id == hc_constants.MORK:
      await message.delete()
      return
    if message.reference:
      messageReference = await channel.fetch_message(message.reference.message_id)
      if reaction.member == messageReference.author and message.author.id == hc_constants.MORK:
        await message.delete()
        return

@bot.event
async def on_thread_create(thread):
    try:
        await thread.join()
    except:
        print("Can't join that thread.")

# # debug
# @bot.event
# async def on_message(message):
# # debug
#   return
#   if (message.author == client.user
#       or message.author.bot
#       or message.author.id in bannedUserIds):
#     return
#   #if message.channel.id == hc_constants.SUBMISSIONS_CHANNEL and len(message.attachments) > 0:
#   #  await message.add_reaction("👍")
#   #  await message.add_reaction("👎")
#   if message.channel.id == hc_constants.HELLS_UNO_CHANNEL:
#     await message.add_reaction("👍")
#     await message.add_reaction("👎")
#   if message.channel.id == hc_constants.VETO_CHANNEL or message.channel.id == hc_constants.EDH_POLLS_CHANNEL:
#     await message.add_reaction("👍")
#     await message.add_reaction(bot.get_emoji(hc_constants.CIRION_SPELLING))
#     await message.add_reaction("👎")
#     await message.add_reaction(bot.get_emoji(hc_constants.MANA_GREEN))
#     await message.add_reaction(bot.get_emoji(hc_constants.MANA_WHITE))
#     await message.add_reaction("🤮")
#     await message.add_reaction("🤔")
#     thread = await message.create_thread(name=message.content)
#     role = get(message.author.guild.roles, id=int(798689768379908106))
#     await thread.send(role.mention)
# ##    for user in role.members:
# ##        await thread.add_user(user)
# ##        await asyncio.sleep(1)
#   if message.channel.id == hc_constants.FOUR_ZERO_ERRATA_SUBMISSIONS_CHANNEL:
#     if "@" in message.content:
#         return
#     sentMessage = await message.channel.send(content = message.content)
#     await sentMessage.add_reaction("👍")
#     await sentMessage.add_reaction("👎")
#     await message.delete()
#   if message.channel.id == hc_constants.SUBMISSIONS_CHANNEL and len(message.attachments) > 0:
#     # debug time, don't double submission management
#     return
#     if "@" in message.content:
#         return
#     file = await message.attachments[0].to_file()
#     sentMessage = await message.channel.send(content = message.content + " by " + message.author.mention, file = file)
#     await sentMessage.add_reaction("👍")
#     await sentMessage.add_reaction("👎")
#     await sentMessage.add_reaction("❌")
#     await message.delete()
#   if message.channel.id == hc_constants.ZBEAN_ICON_CHANNEL:
#     role = get(message.author.guild.roles, id=int(770642233598672906))
#     await message.author.add_roles(role)
#   if "{{" in message.content:
#     await printCardImages(message)
#   try:
#     await bot.process_commands(message)
#   except:
#     ...



# TODO: is this used???
#@bot.command()
#async def removeallchecks(ctx):
#  timeNow = datetime.now(timezone.utc)
#  timeNow = timeNow.replace(tzinfo=None)
#  duration = timeNow + timedelta(days=-30)
#  await ctx.send("Working on it. This may take a bit.")
#  if ctx.channel.id == hc_constants.VETO_DISCUSSION_CHANNEL:
#    messages = bot.get_channel(hc_constants.VETO_CHANNEL).history(after=duration, limit=None)
#    messages = await messages.flatten()
#    for i in range(len(messages)):
#      await messages[i].remove_reaction("✅", bot.get_user(hc_constants.MORK))
#    await ctx.send("removed all my recent ✅ from #veto-polls")

def vetoAnnouncementHelper(cardArray, announcement, annIndex):
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
async def compileveto(ctx):
  if ctx.channel.id == hc_constants.VETO_DISCUSSION_CHANNEL:
    vetoChannel = bot.get_channel(hc_constants.VETO_CHANNEL)
    vetoDiscussionChannel = bot.get_channel(hc_constants.VETO_DISCUSSION_CHANNEL)
    cardListChannel = bot.get_channel(hc_constants.FOUR_ONE_CARD_LIST_CHANNEL)
    timeNow = datetime.now(timezone.utc)  
##    timeNow = timeNow.replace(tzinfo=None)
    twoWeekAgo = timeNow + timedelta(days=-28)
    epicCatchphrases = ["If processing lasts more than 5 minutes, consult your doctor.", "on it, yo.", "ya ya gimme a sec", "processing...", "You're not the boss of me", "ok, 'DAD'", "but what of the children?", "?", "workin' on it!", "on it!", "can do, cap'n!", "raseworter pro tip: run it back, but with less 'tude next time.", "who? oh yeah sure thing b0ss", "how about no for a change?", "CAAAAAAAAAAAAAAN DO!", "i'm afraid i can't let you do that.", "i mean like, if you say so, man", "WOOOOOOOOOOOOOOOOOOOOOOOOOOOO", "*nuzzles u*"]
    await ctx.send(random.choice(epicCatchphrases))
    messages = vetoChannel.history(after=twoWeekAgo, limit=None)
    print(messages)
    if messages is None:
      return
    messages = [message async for message in messages]
    acceptedCards = []
    errataedCards = []
    vetoedCards = []
    earlyCards = []
    vetoHell = []
    for i in range(len(messages)):
      try:
        upvote = get(messages[i].reactions, emoji="👍").count
      except:
        upvote = -1
      try:
        downvote = get(messages[i].reactions, emoji="👎").count
      except:
        downvote = -1
      try:
        errata = get(messages[i].reactions, emoji=bot.get_emoji(hc_constants.CIRION_SPELLING)).count
      except:
        errata = -1
      if (len(messages[i].attachments) == 0):
        continue
      messageAge = timeNow - messages[i].created_at
      if get(messages[i].reactions, emoji="✅") or get(messages[i].reactions, emoji="❌"):
        continue
      elif (messageAge < timedelta(days=1)):
        earlyCards.append(messages[i])

      elif (errata > 4 and errata >= upvote and errata >= downvote):
        errataedCards.append(messages[i])
        await messages[i].add_reaction("✅")
        thread = messages[i].guild.get_channel_or_thread(messages[i].id)
        await thread.edit(archived = True)

      elif (upvote > 4 and upvote >= downvote and upvote >= errata):
        acceptedCards.append(messages[i])
        await messages[i].add_reaction("✅")
        thread = messages[i].guild.get_channel_or_thread(messages[i].id)
        await thread.edit(archived = True)
        file = await messages[i].attachments[0].to_file()
        copy = await messages[i].attachments[0].to_file()
        acceptanceMessage = messages[i].content
        if (len(acceptanceMessage)) == 0:
          acceptanceMessage = "**Crazy card with no name and no author**"
          dbname = ""
          dbauthor = ""
        elif (acceptanceMessage[0:3] == "by "):
          acceptanceMessage = "**Silly card with no name** " + acceptanceMessage
          dbname = ""
          dbauthor = str((acceptanceMessage.split("by "))[1])
        else:
          thisLine = acceptanceMessage.split(" by ")
          for i in range(len(thisLine)):
            if i == 0:
              acceptanceMessage = "**" + thisLine[0] + "**"
              dbname = str(thisLine[0])
              dbauthor = ""
            else:
              acceptanceMessage += " by " + thisLine[i]
              dbauthor = str(thisLine[i])

        sentMessage = await cardListChannel.send(content=acceptanceMessage, file=copy)
        dburl = sentMessage.attachments[0].url
        allCardNames = cardSheetUnapproved.col_values(1)
        newCard = True
        if dbname in allCardNames and dbname != "":
          dbrow = allCardNames.index(dbname) + 1
          newCard = False
        else:
          dbrow = len(allCardNames) + 1
          if dbname == "":
            dbname = "NO NAME"
        cardSheetUnapproved.update_cell(dbrow, 4, dburl)
        if newCard:
          cardSheetUnapproved.update_cell(dbrow, 1, dbname)
          cardSheetUnapproved.update_cell(dbrow, 6, dbauthor)
          boldRangesA1 = [gspread.utils.rowcol_to_a1(dbrow, 1), gspread.utils.rowcol_to_a1(dbrow, 4), gspread.utils.rowcol_to_a1(dbrow, 6)]
          cardSheetUnapproved.format(boldRangesA1, {'textFormat': {'bold': True}})
        else:
          cardSheetUnapproved.format(gspread.utils.rowcol_to_a1(dbrow, 4), {'textFormat': {'bold': True}})
          italicsRangesA1 = []
          thisRow = cardSheetUnapproved.row_values(dbrow)
          print(thisRow)
          for i in range(len(thisRow)):
            if thisRow[i] != "" and i != 0 and i != 3 and i != 5:
              italicsRangesA1.append(gspread.utils.rowcol_to_a1(dbrow, i + 1))
          if italicsRangesA1 != []:
            cardSheetUnapproved.format(italicsRangesA1, {'textFormat': {'italic': True}})


      elif (downvote > 4 and downvote >= upvote and downvote >= errata):
        vetoedCards.append(messages[i])
        await messages[i].add_reaction("✅")

      elif (messageAge > timedelta(days=3)):
        thread = messages[i].guild.get_channel_or_thread(messages[i].id)
        role = get(messages[i].guild.roles, id=int(798689768379908106))
        await thread.send(role.mention)
        vetoHell.append(messages[i])
##        await messages[i].add_reaction("❗")
##        await messages[i].add_reaction("❌")

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

##    for vetoedCard in vetoHell:
##      file = await vetoedCard.attachments[0].to_file()
##      copy = await vetoedCard.attachments[0].to_file() # i have no idea why the function to repost card messages was coded with this weird "copy" thing. If you're reading this, help.
##      cardMessage = vetoedCard.content
##      await vetoChannel.send(content=cardMessage, file=copy)

    print(announcement)
    for i in announcement:
      await vetoDiscussionChannel.send(content=i)

  else:
    await ctx.send("Veto Council Only")

@bot.command(aliases=['awardkisses'])
async def awardkiss(ctx, user, number = 1):
  moderators_list = KissSheet.col_values(1)
  print(ctx.author.id)
  print(moderators_list)
  print(ctx.author.id in moderators_list)
  if str(ctx.author.id) in moderators_list:
    member = await commands.MemberConverter().convert(ctx, user)
    members_list = KissSheet.col_values(2)
    print(members_list)
    print(str(member.id))
    if str(member.id) in members_list:
      row = members_list.index(str(member.id)) + 1
    else:
      row = len(members_list) + 1
      KissSheet.update_cell(row, 2, str(member.id))
      KissSheet.update_cell(row, 3, 0)
      KissSheet.update_cell(row, 4, 0)
      KissSheet.update_cell(row, 5, 0)

    currentKisses = int(KissSheet.cell(row, 3).value) + number
    lifetimeKisses = int(KissSheet.cell(row, 4).value) + number
    KissSheet.update_cell(row, 3, currentKisses)
    KissSheet.update_cell(row, 4, lifetimeKisses)
    await ctx.send(str(user) + " earned " + str(number) + " kisses! Total: " + str(currentKisses) + ". \nUse !kiss @user to give a kiss, or !kisses to check your lifetime kiss stats.")
  else:
    await ctx.send("Only verified kiss arbiters can award kisses! Talk to Zaxer to inquire about becoming a verified kiss arbiter.")

@bot.command()
async def kiss(ctx, user):
  kissers_list = KissSheet.col_values(2)
  if str(ctx.author.id) in kissers_list:
    row = kissers_list.index(str(ctx.author.id)) + 1
    kissCount =  int(KissSheet.cell(row, 3).value)
    if kissCount > 0:
      try:
        KissedMember = await commands.MemberConverter().convert(ctx, user)
      except:
        await ctx.send("Something went wrong. Be sure to ping the user you want me to kiss! Maybe that's what went wrong?")
      if (KissedMember == ctx.author):
        await ctx.send("You can't send a kiss to yourself! How would that even work??")
        return
      if str(KissedMember.id) in kissers_list:
        kissedrow = kissers_list.index(str(KissedMember.id)) + 1
      else:
        kissedrow = len(kissers_list) + 1
        KissSheet.update_cell(kissedrow, 2, str(KissedMember.id))
        KissSheet.update_cell(kissedrow, 3, 0)
        KissSheet.update_cell(kissedrow, 4, 0)
        KissSheet.update_cell(kissedrow, 5, 0)
      KissSheet.update_cell(kissedrow, 5, int(KissSheet.cell(kissedrow, 5).value) + 1)
      MessageList = ["mmmmwah!", "mwah!", "smooch!", "*kisses u*", "mwa!", "dis a kis from me to u :)", "^3^ mweh!", ":*", ";*", "just a quick peck, to be safe- mwa!", "໒(∗ ⇀ 3 ↼ ∗)७", "mwah!"]
      ThisKiss = random.choice(MessageList)
      await ctx.send(user + " " + ThisKiss)
      KissSheet.update_cell(row, 3, kissCount - 1)

    else:
      await ctx.send("You don't have any kisses to send!")
  else:
    await ctx.send("You don't have any kisses to send!")

@bot.command()
async def kisses(ctx):
  kissers_list = KissSheet.col_values(2)
  if str(ctx.author.id) in kissers_list:
    row = kissers_list.index(str(ctx.author.id)) + 1
    current = KissSheet.cell(row, 3).value
    lifetime = KissSheet.cell(row, 4).value
    kissed = KissSheet.cell(row, 5).value
    await ctx.send(f'''You have {current} kisses to give!
You have earned {lifetime} kisses in total!
You have been kissed {kissed} times!''')
  else:
    await ctx.send("You have 0 kisses to give!\nYou have earned 0 kisses in total!\nYou have been kissed 0 times!")


bot.run(DISCORD_ACCESS_TOKEN)
