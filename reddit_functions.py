
import asyncpraw

from secrets.reddit_secrets import ID,SECRET,PASSWORD,USER_AGENT,NAME

async def postToReddit(title:str, image_path:str, flair:str=""):

    reddit = asyncpraw.Reddit(
        client_id=ID,
        client_secret=SECRET,
        password=PASSWORD,
        user_agent=USER_AGENT,
        username=NAME
    )
    # print(await reddit.user.me())
    hellscubeSubreddit:asyncpraw.reddit.Subreddit = await reddit.subreddit('HellsCube')
    
    await hellscubeSubreddit.submit_image(title,image_path,flair_id=flair)
    ## Do stuff with module/file

    
