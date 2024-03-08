
import discord
from discord.utils import get
from discord.ext import commands
import asyncio
import random
import gspread
import pprint as pp
from datetime import datetime, timezone, timedelta

# todo: test this
global cardList
from CardClasses import Side, cardSearch
from shared_vars import cardList,intents,googleClient,drive
import is_mork
from secrets.discord_token import DISCORD_ACCESS_TOKEN
import hc_constants



class MyBot(commands.Bot):
    async def setup_hook(self):
        print('This is asynchronous!')
        initialExtensions = [
          'cogs.SpecificCards',
          'cogs.Messages',
          'cogs.Roles',
          'cogs.Lifecycle',
          'cogs.ZaxersKisses',
          'cogs.Quotes',
          'cogs.HellscubeDatabase'
          ]
        for i in initialExtensions:
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


statusList = ["Haha Gottem in 2024", "Hugh Man in EDH", "the funny dreadmaw card", "Hellscube Victory in Competative", "with old companion rules", "Obama tribal EDH", "irefeT tribal", "Temple of @creator", "cheat big shit out", "v1.0", "2/3 Corpse Knight", "Forbiddenest Ritual for value", "71 lands and Haha Gottem", "PICKLE K'RRIK!", "\"colorless\" card draw", "HellsEdh", "hellscube", "Hellscube Jumpstart", "comboless Zero with Nothing", "with MaRo's feelings", "with Exalted's sanity", "Slot Filler for draw cards equal to 2 minus one", "Epicnessbrian tribal", "a minigame", "a subgame", "a supergame", "The First Pick", "Tendrils of Shahrazad", "hide and seek with Liu Bei's wallet", "with slots", "Redundant Acceleration for 1 card", "with !podcast", "with #brainstorming-shitposts", "with no banlist", "Hatebear With Useful Abilities", "JacobsRedditUsername Tribal", "white card draw!!1!?1!??!?", "Force of Bill for 5 mana", "with bears. So... many... bears...", "Epic Games", "6-mana 1/1s", "a full playset of worm", "all of the murder but _ cycle", "with the idea of skipping to 3.0", "1 cmc super friends", "all the creator lands", "strip hellscube vintage", "cooldownguy vintage", "6-color goodstuff", "a 41 card draft deck", "infinite basics in the sideboard", "10.000 Islands in the main", "#avatar in discord", "Avatar of Discord, Please spam Attack. Please", "Avatar of Discord, Please spam Defence. Please", "Avatar of Discord, Please spam Evasion. Please", "Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing Bears Repeating Playing...", "blue bears"]

global blueRed
blueRed = False

cardSheetSearch = googleClient.open("Hellscube Database").worksheet("Database Bot Read")

cardsDataSearch = cardSheetSearch.col_values(2)



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
    upvote = get(messages[i].reactions, emoji=hc_constants.VOTE_UP)
    downvote = get(messages[i].reactions, emoji=hc_constants.VOTE_DOWN)
    messageAge = timeNow - messages[i].created_at
    if upvote and downvote:
      upCount = upvote.count
      downCount = downvote.count
      #if (upvote.count - downvote.count) < -10 and len(messages[i].attachments) > 0 and messageAge >= timedelta(days=1):
      #  await messages[i].delete()
      if (upCount - downCount) > 24 and len(messages[i].attachments) > 0 and messageAge >= timedelta(days=1) and is_mork.is_mork(messages[i].author.id):
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
    upvote = get(messages[i].reactions, emoji=hc_constants.VOTE_UP)
    downvote = get(messages[i].reactions, emoji=hc_constants.VOTE_DOWN)
    messageAge = timeNow - messages[i].created_at
    if upvote and downvote:
      upCount = upvote.count
      downCount = downvote.count
      if (upCount - downCount) > 14 and messageAge >= timedelta(days=1):
        acceptContent = messages[i].content
        await acceptedChannel.send(content=acceptContent)
        await messages[i].add_reaction("✅")
  print("------done checking errata submissions-----")

# not sure what all of this next stuff is
  
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
#      upvote = get(messages[i].reactions, emoji=hc_constants.VOTE_UP)
#      downvote = get(messages[i].reactions, emoji=hc_constants.VOTE_DOWN)
#      if len(messages[i].attachments) > 0 and is_mork(messages[i].author.id):
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
#     await sentMessage.add_reaction(hc_constants.VOTE_UP)
#     await sentMessage.add_reaction(hc_constants.VOTE_DOWN)
#     await sentMessage.add_reaction("❌")

##@bot.command()
##async def morkPost(ctx, messageID):
##   message = await ctx.fetch_message(messageID)
##   subchannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
##   mork = bot.get_user(hc_constants.MORK)
##   file = await message.attachments[0].to_file()
##   sentMessage = await subchannel.send(content=message.content + " by " + mork.mention, file=file)
##   await sentMessage.add_reaction(hc_constants.VOTE_UP)
##   await sentMessage.add_reaction(hc_constants.VOTE_DOWN)
##   await sentMessage.add_reaction("❌")

log = ""

@bot.command(name="dumplog")
async def _dumplog(ctx:commands.Context):
    global log
    if ctx.author.id == hc_constants.EXALTED_ONE:
        with open("log.txt", 'a', encoding='utf8') as file:
            file.write(log)
            log = ""
            print("log dumped")

@bot.command()
async def getMessage(ctx:commands.Context, id):
  subChannel = bot.get_channel(hc_constants.SUBMISSIONS_CHANNEL)
  message = await subChannel.fetch_message(id)
  await ctx.send(message.jump_url)


FIVE_MINUTES=300

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
    await asyncio.sleep(FIVE_MINUTES)

@bot.command()
async def macro(ctx:commands.Context, thing:str, *args):
  if thing == "help":
    message = "Macros are:\nJoke [word]\n"
    for name in hc_constants.macroList.keys():
      if type(hc_constants.macroList[name]) is str:
        message += f"{name}\n"
      else:
        message += f"{name}\n"
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
async def gameNight(ctx:commands.Context, mode, game):
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
      result += f"{games[i]: {str(amount[i])}}\n"
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
async def goodbye(ctx:commands.Context):
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
async def BlueRed(ctx:commands.Context):
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
async def menu(ctx:commands.Context):
  if ctx.channel.id == hc_constants.RESOURCES_CHANNEL or hc_constants.BOT_TEST_CHANNEL:
    embed = discord.Embed(title="Resources Menu", description="[Channel Explanation](https://discord.com/channels/631288872814247966/803384271766683668/803384426360078336)\n[Command List](https://discord.com/channels/631288872814247966/803384271766683668/803389199503982632)\n[Achievements](https://discord.com/channels/631288872814247966/803384271766683668/803389622247882782)\n[Database](https://discord.com/channels/631288872814247966/803384271766683668/803390530145878057)\n[Release Notes](https://discord.com/channels/631288872814247966/803384271766683668/803390718801346610)\n[Cubecobras](https://discord.com/channels/631288872814247966/803384271766683668/803391239294025748)\n[Tabletop Simulator](https://discord.com/channels/631288872814247966/803384271766683668/803391314095636490)")
    await ctx.send(embed=embed)

@bot.command()
async def help(ctx:commands.Context):
  await ctx.send("https://discord.com/channels/631288872814247966/803384271766683668/803389199503982632")

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
async def compileveto(ctx:commands.Context):
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
        upvote = get(messages[i].reactions, emoji=hc_constants.VOTE_UP).count
      except:
        upvote = -1
      try:
        downvote = get(messages[i].reactions, emoji=hc_constants.VOTE_DOWN).count
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

      elif (errata > 4
            and errata >= upvote
            and errata >= downvote):
        errataedCards.append(messages[i])
        await messages[i].add_reaction("✅")
        thread = messages[i].guild.get_channel_or_thread(messages[i].id)
        await thread.edit(archived = True)

      elif (upvote > 4
            and upvote >= downvote
            and upvote >= errata):
        acceptedCards.append(messages[i])
        await messages[i].add_reaction("✅")
        thread = messages[i].guild.get_channel_or_thread(messages[i].id)
        await thread.edit(archived = True)
        file = await messages[i].attachments[0].to_file() # lol okay here's the other weird file and copy
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
    ## I'm sorry, i can't help. oh shit i deleted a copy line a while ago. hope we didnit need that
##      cardMessage = vetoedCard.content
##      await vetoChannel.send(content=cardMessage, file=copy)

    print(announcement)
    for i in announcement:
      await vetoDiscussionChannel.send(content=i)

  else:
    await ctx.send("Veto Council Only")


bot.run(DISCORD_ACCESS_TOKEN)
