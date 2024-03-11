


import os

import asyncpraw
from discord import File

from secrets.reddit_secrets import ID,SECRET,PASSWORD,USER_AGENT,NAME

async def postToReddit(title:str, file:File, flair:str=""):
    image_path = f'tempImages/{file.filename}'
    with open(image_path, 'wb') as out: ## Open temporary file as bytes
        out.write(file.fp.read())  ## Read bytes into file


    reddit = asyncpraw.Reddit(
        client_id=ID,
        client_secret=SECRET,
        password=PASSWORD,
        user_agent=USER_AGENT,
        username=NAME
    )
    # print(await reddit.user.me())
    hellscubeSubreddit = await reddit.subreddit('HellsCube')
    
    await hellscubeSubreddit.submit_image(title,image_path,flair_id=flair)
    ## Do stuff with module/file

    
    os.remove(image_path) ## Delete file when done
