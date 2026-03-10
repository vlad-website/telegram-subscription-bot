from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    text = (
        """Привет! 👋  

Добро пожаловать в закрытый клуб  
✨ «Разная» — пространство, где женщина может быть собой.

Здесь не нужно выбирать между:  
💪 «сильной» и 🌸 «нежной»  
🧠 «умной» и 💃 «красивой»  
💼 «работать» и ❤️ «чувствовать»

Здесь можно быть разной:  
настоящей, настроенческой, живой,  
настроенной на жизнь, любовь, спорт и здоровье. ✨

Каждый месяц в клубе тебя ждут:  
🔥 новые темы  
🏋️‍♀️ новые тренировки  
💡 новые советы и секреты  
🧘‍♀️ практики и разговоры, после которых  
хочется жить, а не выживать.

Ты можешь выбрать подписку  
📅 на 1 месяц или на 3 месяца  
и войти в сообщество женщин, которые идут к себе.

Если ты готова — давай начнём! 💫"""
    )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard()
    )