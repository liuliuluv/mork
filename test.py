import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from threading import Timer
import re

from shared_vars import drive
a='inline;filename="                                Skald.png"'

print(re.findall('="(.*)"',a))