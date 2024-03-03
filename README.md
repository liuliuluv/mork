
I have no idea what is going on, Exalted built this.


# Setup
1. Install dependencies via `pip install -r requirements.txt`
1. Make a new Discord application and invite it to the server
1. The bot will need OAuth2 scopes of bot and applications.commands
1. Bot permissions will need read/write messages, read message history, and send messages
1. Make a copy of `discord_token.template.py` called `discord_token.py`. Add the bot token




# To get it to work
to get a copy to work you'd have to do a few things
- Make a new Discord application on the dev portal and invite it to the server. Replace the token in the code with the new token.
- Make a Google Service Account and invite it to the Hellscube Database spreadsheet. Put its credentials somewhere so they can loaded.
- Do the authentication part https://pythonhosted.org/PyDrive/quickstart.html so that the quote and gamenight commands work. Also change the file ids.






