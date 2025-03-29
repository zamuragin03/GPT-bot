import configparser
from pathlib import Path
import sys

config = configparser.ConfigParser()
PATH = Path(__file__).resolve().parent

config.read(str(PATH) + '/config.ini')
if sys.argv[1] == '--build':
    config.read(str(PATH) + '/config_build.ini')

if sys.argv[1] == '--dev':
    config.read(str(PATH) + "/config_dev.ini")
BOT_TOKEN = config["Telegram"]["bot_token"]

PATH_TO_TEMP_WATERMARK = PATH.joinpath('watermark.png')
PATH_TO_TEMP_FILES = PATH.parent.joinpath('Users_Files')
PATH_TO_DOWNLOADED_FILES = PATH.parent.joinpath('Users_Sent_Files')
PATH_TO_LOCALIZATION = PATH.parent.joinpath('Localization')
PROXY = config["Telegram"]["proxy"]
AUTH_TOKEN = config["Telegram"]["auth_token"]
OPENAI_TOKEN = config["Telegram"]["openai_key"]
PAYMENT_SHOP_ID = config['Payments']['PAYMENT_SHOP_ID']
PAYMENT_KEY = config['Payments']['PAYMENT_KEY']
ANTI_PLAGIAT_API = config['API']['antiplagiat_api']
X_USER_ID = config['API']['user_id']
SERVICE_CHAT_ID = 0
GROUP_LINK_URL = "https://t.me/student_helper_news"
UNLIMITED = 99999
NO_ACCESS = 0

SUBSCRIPTION_LIMITATIONS = {
    "default_mode": UNLIMITED,
    "code_helper": UNLIMITED,
    "chart_creator_helper": UNLIMITED,
    "anti_plagiarism_system":1,
    "abstract_writer": 1,
    "course_work_helper": 1,
    "final_paper_helper": 1,
    "essay_helper": 1,
    "photo_issue_helper": 3,
    "power_point_helper": 3,
    "rewriting_helper": 2,
}

DAILY_LIMITATIONS = {
    "default_mode": 10,
    "code_helper": NO_ACCESS,
    "chart_creator_helper": NO_ACCESS,
    "abstract_writer": NO_ACCESS,
    "course_work_helper": NO_ACCESS,
    "final_paper_helper": NO_ACCESS,
    "essay_helper": NO_ACCESS,
    "photo_issue_helper": NO_ACCESS,
    "power_point_helper": NO_ACCESS,
    "rewriting_helper": NO_ACCESS,
    "anti_plagiarism_system": NO_ACCESS,
}


from enum import Enum

class AI_MODELS(Enum):
    O_3_MINI = 'o3-mini'
    GPT_4_O = 'gpt-4o'
    GPT_4_O_MINI = 'gpt-4o-mini'

class REASONING_EFFORT(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGHT = 'high'