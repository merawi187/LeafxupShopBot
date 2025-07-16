import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import os

# Замените на свой токен
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
# Замените на свой ID чата менеджеров
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', '0'))

# Список платформ
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

async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать! Выберите платформу для покупки услуги:",
        reply_markup=get_platforms_keyboard()
    )

async def platform_callback_handler(callback: CallbackQuery):
    if callback.data == "steam":
        await callback.message.answer("Пожалуйста, введите ваш логин Steam:")
        await callback.answer()
        # Сохраняем состояние для дальнейшего ввода
        await callback.message.bot.session.storage.set_data(callback.from_user.id, {"state": "awaiting_steam_login"})
    else:
        await callback.message.answer(f"Вы выбрали: {dict(PLATFORMS)[callback.data]}\n\nПодтвердите заказ?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{callback.data}")))
        await callback.answer()

async def text_handler(message: Message):
    # Проверяем состояние пользователя
    data = await message.bot.session.storage.get_data(message.from_user.id)
    if data and data.get("state") == "awaiting_steam_login":
        login = message.text.strip()
        await message.answer("Введите сумму пополнения в рублях:")
        await message.bot.session.storage.set_data(message.from_user.id, {"state": "awaiting_steam_amount", "login": login})
    elif data and data.get("state") == "awaiting_steam_amount":
        try:
            amount = float(message.text.strip().replace(',', '.'))
            commission = round(amount * 0.08, 2)
            total = round(amount + commission, 2)
            login = data.get("login")
            await message.answer(f"Логин: {login}\nСумма пополнения: {amount}₽\nКомиссия (8%): {commission}₽\nИтого к оплате: {total}₽\n\nПодтвердить заказ?", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Подтвердить", callback_data="confirm_steam")))
            await message.bot.session.storage.set_data(message.from_user.id, {"state": "confirm_steam", "login": login, "amount": amount, "commission": commission, "total": total})
        except ValueError:
            await message.answer("Пожалуйста, введите корректную сумму в рублях.")
    else:
        await message.answer("Пожалуйста, выберите платформу через меню /start.")

async def confirm_callback_handler(callback: CallbackQuery):
    if callback.data.startswith("confirm_"):
        platform = callback.data.replace("confirm_", "")
        if platform == "steam":
            data = await callback.message.bot.session.storage.get_data(callback.from_user.id)
            login = data.get("login")
            amount = data.get("amount")
            commission = data.get("commission")
            total = data.get("total")
            text = f"[НОВЫЙ ЗАКАЗ]\nSteam\nЛогин: {login}\nСумма: {amount}₽\nКомиссия: {commission}₽\nИтого: {total}₽\nПользователь: @{callback.from_user.username or 'Без username'} ({callback.from_user.id})"
        else:
            text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {dict(PLATFORMS)[platform]}\nПользователь: @{callback.from_user.username or 'Без username'} ({callback.from_user.id})"
        await callback.message.bot.send_message(MANAGER_CHAT_ID, text)
        await callback.message.answer("Спасибо за заказ! С вами свяжется менеджер для оплаты.")
        await callback.answer()
        await callback.message.bot.session.storage.set_data(callback.from_user.id, {})

async def main():
    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # Простое хранилище в памяти для состояний пользователей
    class SimpleStorage:
        def __init__(self):
            self.data = {}
        async def set_data(self, user_id, value):
            self.data[user_id] = value
        async def get_data(self, user_id):
            return self.data.get(user_id, {})
    bot.session = types.SimpleNamespace(storage=SimpleStorage())

    dp.message.register(start_handler, Command("start"))
    dp.callback_query.register(platform_callback_handler, lambda c: c.data in [p[0] for p in PLATFORMS])
    dp.callback_query.register(confirm_callback_handler, lambda c: c.data.startswith("confirm_"))
    dp.message.register(text_handler)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 