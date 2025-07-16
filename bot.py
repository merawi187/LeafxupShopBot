import os
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', '0'))

bot = telebot.TeleBot(BOT_TOKEN)

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

user_states = {}

# Клавиатура выбора платформы
def get_platforms_keyboard():
    kb = types.InlineKeyboardMarkup()
    for callback, name in PLATFORMS:
        kb.add(types.InlineKeyboardButton(text=name, callback_data=callback))
    return kb

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите платформу для покупки услуги:", reply_markup=get_platforms_keyboard())

@bot.callback_query_handler(func=lambda call: call.data in [p[0] for p in PLATFORMS])
def platform_callback_handler(call):
    if call.data == "steam":
        user_states[call.from_user.id] = {"state": "awaiting_steam_login"}
        bot.send_message(call.message.chat.id, "Пожалуйста, введите ваш логин Steam:")
    else:
        user_states[call.from_user.id] = {"state": f"confirm_{call.data}"}
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{call.data}"))
        bot.send_message(call.message.chat.id, f"Вы выбрали: {dict(PLATFORMS)[call.data]}\n\nПодтвердите заказ?", reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "awaiting_steam_login")
def steam_login_handler(message):
    login = message.text.strip()
    user_states[message.from_user.id] = {"state": "awaiting_steam_amount", "login": login}
    bot.send_message(message.chat.id, "Введите сумму пополнения в рублях:")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "awaiting_steam_amount")
def steam_amount_handler(message):
    try:
        amount = float(message.text.strip().replace(',', '.'))
        commission = round(amount * 0.08, 2)
        total = round(amount + commission, 2)
        login = user_states[message.from_user.id]["login"]
        user_states[message.from_user.id] = {
            "state": "confirm_steam",
            "login": login,
            "amount": amount,
            "commission": commission,
            "total": total
        }
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Подтвердить", callback_data="confirm_steam"))
        bot.send_message(message.chat.id, f"Логин: {login}\nСумма пополнения: {amount}₽\nКомиссия (8%): {commission}₽\nИтого к оплате: {total}₽\n\nПодтвердить заказ?", reply_markup=kb)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректную сумму в рублях.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_callback_handler(call):
    platform = call.data.replace("confirm_", "")
    username = call.from_user.username or 'Без username'
    if platform == "steam":
        data = user_states.get(call.from_user.id, {})
        login = data.get("login")
        amount = data.get("amount")
        commission = data.get("commission")
        total = data.get("total")
        text = f"[НОВЫЙ ЗАКАЗ]\nSteam\nЛогин: {login}\nСумма: {amount}₽\nКомиссия: {commission}₽\nИтого: {total}₽\nПользователь: @{username} ({call.from_user.id})"
    else:
        text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {dict(PLATFORMS)[platform]}\nПользователь: @{username} ({call.from_user.id})"
    bot.send_message(MANAGER_CHAT_ID, text)
    bot.send_message(call.message.chat.id, "Спасибо за заказ! С вами свяжется менеджер для оплаты.")
    user_states.pop(call.from_user.id, None)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    bot.send_message(message.chat.id, "Пожалуйста, выберите платформу через меню /start.")

if __name__ == "__main__":
    bot.polling(none_stop=True) 