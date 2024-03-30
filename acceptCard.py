import os
import re
from typing import cast
import discord
import hc_constants
from is_mork import getDriveUrl, uploadToDrive
from shared_vars import googleClient
from discord.ext import commands


from reddit_functions import postToReddit

cardSheetUnapproved = googleClient.open_by_key(hc_constants.HELLSCUBE_DATABASE).worksheet("Kopie van Database")


async def acceptCard(bot:commands.Bot, cardMessage:str, file:discord.File, cardName:str, authorName:str):
    cardListChannel = cast(discord.TextChannel, bot.get_channel(hc_constants.FOUR_ONE_CARD_LIST_CHANNEL))
    await cardListChannel.send( file = file, content = cardMessage)

    extension = re.search("\.([^.]*)$", file.filename)  # this code sucks but i don't remember what the discord file object looks like

    fileType = extension.group() if extension else ".png" # just guess that the file is a png

    image_path = f'tempImages/{cardName.replace("/", "|")}{fileType}'

    with open(image_path, 'wb') as out:
        out.write(file.fp.read())

    try:
        # There used to be a try/catch here, but it turned out that reddit was not the flakiest part here. it was llllll
        await postToReddit(
            image_path,
            title = f"{cardMessage} was accepted!",
            flair = hc_constants.ACCEPTED_FLAIR
        )
    except Exception as e:
        print("tried to post to reddit", e)

    google_drive_file_id = uploadToDrive(image_path)

    os.remove(image_path)

    imageUrl = getDriveUrl(google_drive_file_id)

    allCardNames = cardSheetUnapproved.col_values(1)

    newCard = True
    if cardName in allCardNames and cardName != "":
        dbRowIndex = allCardNames.index(cardName) + 1
        newCard = False
    else:
        dbRowIndex = len(allCardNames) + 1
        if cardName == "":
            cardName = "NO NAME"

    cardSheetUnapproved.update_cell(dbRowIndex, 2, imageUrl)
    
    if newCard:
        cardSheetUnapproved.update_cell(dbRowIndex, 1, cardName)
        cardSheetUnapproved.update_cell(dbRowIndex, 3, authorName)