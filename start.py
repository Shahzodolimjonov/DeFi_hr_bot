from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart

import content
from config import BOT_TOKEN
from keyboard import menu_kb

bot = Bot(token=BOT_TOKEN)
router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(content.start_talk, reply_markup=menu_kb())
