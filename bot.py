import os
import telebot
from telebot import types
from dotenv import load_dotenv
import threading
from flask import Flask

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', '0'))

bot = telebot.TeleBot(BOT_TOKEN)

# Товары Genshin Impact
GENSHIN_ITEMS = [
    ("Гимн", 700),
    ("Хор", 1410),
    ("Х65", 70),
    ("Х300", 310),
    ("Х980", 980),
    ("Х1980", 1850),
    ("Х3280", 2900),
    ("Х6480", 5800),
    ("Карточка", 310)
]

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

PLATFORM_PHOTOS = {
    "genshin_price": ("genshin_price.jpg", "Прайс-лист Genshin Impact"),
    "genshin_locations": ("genshin_locations.jpg", "Прайс-лист Genshin Impact (закрытие локаций)"),
    "steam": ("steam.jpg", "Прайс-лист Steam"),
    "hsr_price": ("honkai_price.jpg", "Прайс-лист Honkai: Star Rail"),
    "zzz_price": ("zzz_price.jpg", "Прайс-лист Zenless Zone Zero"),
    "roblox_price": ("roblox_price.jpg", "Прайс-лист Roblox"),
    "clash_price": ("coc_price.jpg", "Прайс-лист Clash Of Clans"),
    "brawl_price": ("bs_price.jpg", "Прайс-лист Brawl Stars"),
}

def get_platforms_keyboard():
    kb = types.InlineKeyboardMarkup()
    for callback, name in PLATFORMS:
        kb.add(types.InlineKeyboardButton(text=name, callback_data=callback))
    return kb

def get_genshin_keyboard():
    kb = types.InlineKeyboardMarkup()
    for item, price in GENSHIN_ITEMS:
        kb.add(types.InlineKeyboardButton(text=f"{item} ({price}₽)", callback_data=f"genshin_{item}"))
    kb.add(types.InlineKeyboardButton(text="Показать прайс-лист", callback_data="genshin_price_photo"))
    return kb

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите платформу для покупки услуги:", reply_markup=get_platforms_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "genshin_price")
def genshin_price_handler(call):
    bot.send_message(call.message.chat.id, "Выберите товар Genshin Impact:", reply_markup=get_genshin_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.endswith("_price_photo") or call.data in PLATFORM_PHOTOS)
def send_platform_photo(call):
    # Универсальный обработчик для всех прайсов по кнопкам
    key = call.data.replace("_photo", "")
    photo_info = PLATFORM_PHOTOS.get(key)
    if photo_info:
        filename, caption = photo_info
        try:
            with open(filename, "rb") as photo:
                bot.send_photo(call.message.chat.id, photo, caption=caption)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Не удалось отправить фото прайса для {caption}. Обратитесь к менеджеру.")
    else:
        bot.send_message(call.message.chat.id, "Прайс-лист скоро будет доступен в виде фото!")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data in PLATFORM_PHOTOS)
def platform_callback_handler_with_photo(call):
    photo_info = PLATFORM_PHOTOS.get(call.data)
    if photo_info:
        filename, caption = photo_info
        try:
            with open(filename, "rb") as photo:
                bot.send_photo(call.message.chat.id, photo, caption=caption)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Не удалось отправить фото прайса для {caption}. Обратитесь к менеджеру.")
    # Genshin Impact: фото + клавиатура с товарами
    if call.data == "genshin_price":
        kb = types.InlineKeyboardMarkup()
        for item, price in GENSHIN_ITEMS:
            kb.add(types.InlineKeyboardButton(text=f"{item} ({price}₽)", callback_data=f"genshin_{item}"))
        bot.send_message(call.message.chat.id, "Выберите товар Genshin Impact:", reply_markup=kb)
    # Genshin Locations: фото + подтверждение
    elif call.data == "genshin_locations":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Подтвердить заказ", callback_data="confirm_genshin_locations"))
        bot.send_message(call.message.chat.id, "Вы выбрали: Genshin Impact (закрытие локаций). Подтвердите заказ:", reply_markup=kb)
    # Steam: фото + запрос логина
    elif call.data == "steam":
        user_states[call.from_user.id] = {"state": "awaiting_steam_login"}
        bot.send_message(call.message.chat.id, "Пожалуйста, введите ваш логин Steam:")
    # Остальные: фото + подтверждение
    elif call.data in ["hsr_price", "zzz_price", "roblox_price", "clash_price", "brawl_price"]:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Подтвердить заказ", callback_data=f"confirm_{call.data}"))
        platform_name = dict(PLATFORMS)[call.data]
        bot.send_message(call.message.chat.id, f"Вы выбрали: {platform_name}. Подтвердите заказ:", reply_markup=kb)
    bot.answer_callback_query(call.id)

# Genshin Impact: обработка выбора товара
@bot.callback_query_handler(func=lambda call: call.data.startswith("genshin_"))
def genshin_item_handler(call):
    item = call.data.replace("genshin_", "")
    for name, price in GENSHIN_ITEMS:
        if item == name:
            bot.send_message(call.message.chat.id, f"Вы выбрали: {name} ({price}₽). Для заказа напишите менеджеру или подтвердите заказ.")
            break
    bot.answer_callback_query(call.id)

# Steam: логин -> сумма с ограничением
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "awaiting_steam_login")
def steam_login_handler(message):
    login = message.text.strip()
    user_states[message.from_user.id] = {"state": "awaiting_steam_amount", "login": login}
    bot.send_message(message.chat.id, "Введите сумму пополнения в рублях (от 100 до 25000):")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "awaiting_steam_amount")
def steam_amount_handler(message):
    try:
        amount = float(message.text.strip().replace(',', '.'))
        if amount < 100 or amount > 25000:
            bot.send_message(message.chat.id, "Сумма должна быть от 100 до 25000 рублей. Попробуйте снова.")
            return
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

# Flask-заглушка для Render

def run_flask():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "OK"

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    bot.polling(none_stop=True) 