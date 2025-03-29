from .const import BOT_TOKEN, PATH_TO_LOCALIZATION, OPENAI_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
import json
from aiogram.client.default import DefaultBotProperties
from openai import AsyncOpenAI

scheduler = AsyncIOScheduler()

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
# dp = Dispatcher(storage=redis_storage)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
gpt_router = Router()
gpt_free_router = Router()
admin_router = Router()
scheduler = AsyncIOScheduler()

TEXT_LOCALIZATION_JSON = {}
BUTTON_LOCALIZATION_JSON = {}
SUBSCRIPTION_LOCALIZATION_JSON = {}

with open(PATH_TO_LOCALIZATION.joinpath('text.localization.json'), 'r') as f:
    TEXT_LOCALIZATION_JSON = json.load(f)

with open(PATH_TO_LOCALIZATION.joinpath('buttons.localization.json'), 'r') as f:
    BUTTON_LOCALIZATION_JSON = json.load(f)

with open(PATH_TO_LOCALIZATION.joinpath('subscription.localization.json'), 'r') as f:
    SUBSCRIPTION_LOCALIZATION_JSON = json.load(f)


client = AsyncOpenAI(
    api_key=OPENAI_TOKEN,
)
