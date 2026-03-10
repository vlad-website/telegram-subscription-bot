from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    text = (
        """Привет! 
Добро пожаловать в закрытый клуб
  "Разная" - пространство, где женщина может быть собой!
Здесь не нужно выбирать между "сильной" и
    "нежной", между "умной" и "красивой", между
    "работать" и "чувствовать".
Здесь можно быть разной, настоящей, настроенческой и настроенной на жизнь, любовь, спорт и здоровье.
    Каждый месяц в клубе тебя ждут:
        - новые темы,
        - новые тренировки,
        - новые советы и секреты,
        - новые практики и разговоры, после которых хочется жить, а не выживать.
Ты можешь выбрать подписку на 1 или на 3 месяца и войти в сообщество женщин, которые идут к себе.
  Если ты готова, тогда давай начнём!"""
    )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard()
    )