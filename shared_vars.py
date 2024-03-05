from typing import Mapping
import discord
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from pydrive2.drive import GoogleDrive
from CardClasses import Card

from login_with_service_account import login_with_service_account


allCards:Mapping[str,Card] = {}

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.guilds = True

gauth = login_with_service_account()
drive = GoogleDrive(gauth)

scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("secrets/client_secrets.json", scope)

googleClient = gspread.authorize(creds)