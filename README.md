
I have no idea what is going on, I think Exalted and cirion built this. (and Zaxer too?)





# Setting up for local development
1. Install dependencies via `pip install -r requirements.txt`
1. Make a copy of `discord_token.template.py` called `discord_token.py`. Add the bot token.
1. Get a copy of `client_secrets.json`
1. `python Mork.py`




# starting the bot from scratch
1. Make a new Discord application and invite it to the server
1. The bot will need OAuth2 scopes of bot and applications.commands
1. Bot permissions will need read/write messages, read message history, and send messages.
1. Ask someone to add the both to the server and give it the bot role too


# To get it to work
to get a copy to work you'd have to do a few things
- Make a new Discord application on the dev portal and invite it to the server. Replace the token in the code with the new token.
- Make a Google Service Account and invite it to the Hellscube Database spreadsheet. Put its credentials somewhere so they can loaded.
- Do the authentication part https://pythonhosted.org/PyDrive/quickstart.html so that the quote and gamenight commands work. Also change the file ids.




# Concepts
Uh go read about discord cogs, just write your feature-specific code in one of those, then reference it in Mork.

If Mork needs to track that it has interacted with a post outside of the submissions channel, it usually uses `await message.add_reaction(hc_constants.ACCEPT)`. It would be super nice to unify that.




# Assorted commands
`nohup python3 Mork.py >/dev/null 2>&1`