from aiogram import Bot, Dispatcher
from utils.config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()