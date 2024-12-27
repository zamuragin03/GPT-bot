import configparser
from pathlib import Path
import sys

config = configparser.ConfigParser()
PATH = Path(__file__).resolve().parent
config.read(str(PATH) + '/config.ini')

BOT_TOKEN = config["Telegram"]["bot_token"]
PATH_TO_DB = PATH.parent.joinpath('DB_volume').joinpath('data.db')
PATH_TO_TEMP_FILES = PATH.parent.joinpath('Users_Files')
PATH_TO_LOCALIZATION = PATH.parent.joinpath('Localization')
PROXY = config["Telegram"]["proxy"]
AUTH_TOKEN = config["Telegram"]["auth_token"]
OPENAI_TOKEN = config["Telegram"]["openai_key"]


SERVICE_CHAT_ID =0


