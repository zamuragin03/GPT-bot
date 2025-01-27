from DBRepository.DBRepository import DBRepository
from .const import BOT_TOKEN, PATH_TO_DB, PATH_TO_LOCALIZATION, OPENAI_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
import json
from openai import AsyncOpenAI
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage

scheduler = AsyncIOScheduler()
bot = Bot(BOT_TOKEN,)
redis = Redis(host='localhost', port=6379, db=5)
redis_storage = RedisStorage(redis=redis)
# dp = Dispatcher(storage=redis_storage)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
Repository = DBRepository(PATH_TO_DB)

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
