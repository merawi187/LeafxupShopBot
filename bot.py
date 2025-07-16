import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Замените на свой токен
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', '0'))

PLATFORMS = [
    ("genshin_price", "💎 Genshin Impact (прайс)"),
    ("genshin_locations", "💎 Genshin Impact (закрытие локаций)"),
    ("steam", "👁 Пополнение аккаунта Steam"),
    ("hsr_price", "🌟 Honkai: Star Rail (прайс)"),
    ("zzz_price", "💎 Zenless Zone Zero (прайс)"),
    ("roblox_price", "💎 Roblox (прайс)"),
    ("clash_price", "💎 Clash Of Clans (прайс)"),
    ("brawl_price", "💎 Brawl Stars (прайс)")
]

def get_platforms_keyboard():
    kb = InlineKeyboardMarkup()
    for callback, name in PLATFORMS:
        kb.add(InlineKeyboardButton(text=name, callback_data=callback))
    return kb

# FSM States
class SteamOrder(StatesGroup):
    waiting_for_login = State()
    waiting_for_amount = State()

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать! Выберите платформу для покупки услуги:",
        reply_markup=get_platforms_keyboard()
    )

@dp.callback_query_handler(lambda c: c.data in [p[0] for p in PLATFORMS])
async def platform_callback_handler(callback: CallbackQuery):
    if callback.data == "steam":
        await callback.message.answer("Пожалуйста, введите ваш логин Steam:")
        await SteamOrder.waiting_for_login.set()
    else:
        await callback.message.answer(f"Вы выбрали: {dict(PLATFORMS)[callback.data]}\n\nПодтвердите заказ?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{callback.data}")))
    await callback.answer()

@dp.message_handler(state=SteamOrder.waiting_for_login)
async def steam_login_handler(message: Message, state: FSMContext):
    login = message.text.strip()
    await state.update_data(login=login)
    await message.answer("Введите сумму пополнения в рублях:")
    await SteamOrder.waiting_for_amount.set()

@dp.message_handler(state=SteamOrder.waiting_for_amount)
async def steam_amount_handler(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip().replace(',', '.'))
        commission = round(amount * 0.08, 2)
        total = round(amount + commission, 2)
        data = await state.get_data()
        login = data.get("login")
        await state.update_data(amount=amount, commission=commission, total=total)
        await message.answer(f"Логин: {login}\nСумма пополнения: {amount}₽\nКомиссия (8%): {commission}₽\nИтого к оплате: {total}₽\n\nПодтвердить заказ?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Подтвердить", callback_data="confirm_steam")))
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму в рублях.")

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
async def confirm_callback_handler(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.replace("confirm_", "")
    if platform == "steam":
        data = await state.get_data()
        login = data.get("login")
        amount = data.get("amount")
        commission = data.get("commission")
        total = data.get("total")
        text = f"[НОВЫЙ ЗАКАЗ]\nSteam\nЛогин: {login}\nСумма: {amount}₽\nКомиссия: {commission}₽\nИтого: {total}₽\nПользователь: @{callback.from_user.username or 'Без username'} ({callback.from_user.id})"
        await state.finish()
    else:
        text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {dict(PLATFORMS)[platform]}\nПользователь: @{callback.from_user.username or 'Без username'} ({callback.from_user.id})"
    await bot.send_message(MANAGER_CHAT_ID, text)
    await callback.message.answer("Спасибо за заказ! С вами свяжется менеджер для оплаты.")
    await callback.answer()

@dp.message_handler()
async def fallback_handler(message: Message):
    await message.answer("Пожалуйста, выберите платформу через меню /start.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True) 