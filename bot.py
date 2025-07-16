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

PLATFORM_TEXTS = {
    "genshin_locations": (
        "💎 Закрытие локаций в Genshin Impact\n"
        "\n🌪 - Мондштадт\n"
        "•  Мондштадт (100 % закрытие) - 850 рублей.\n"
        "• Драконий хребет (100 % закрытие) - 700\n"
        "• Мондштадт/Драконий хребет (100 % закрытие) - 1300\n"
        "\n🪨 - Ли Юэ\n"
        "• Ли Юэ (100 % закрытие) - 2300\n"
        "• Разлом (100 закрытие) - 1000 \n"
        "• Ли Юэ/Разлом (100 % закрытие) - 3300\n"
        "• Долина Чэньюй (100 % закрытие) - 2200\n"
        "\n⚡️ - Инадзума\n"
        "• Инадзума (100 % закрытие) - 2000\n"
        "• Энканомия (100 % закрытие) - 1200\n"
        "• Инадзума/Энканомия (100 % закрытие) - 3200\n"
        "\n🌿 - Сумеру \n"
        "• Сумеру (100 % закрытие) - 2200\n"
        "• Пустыня Колоннад (100 % закрытие) - 1350 \n"
        "• Пустыня Хадрамавет (100 % закрытие) - 1800\n"
        "• Царство Фаракхерт (100 % закрытие) - 1200\n"
        "• Все пустыни Сумеру (100 % закрытие) - 4350 \n"
        "• Сумеру тропики и пустыня (100 % закрытие) - 6500\n"
        "\n🫵 - Фонтейн \n"
        "• Кур Де Фонтейн (100 % закрытие) - 1800\n"
        "• Институт Фонтейна (100 % закрытие) - 1700 \n"
        "• Лес Эриний (100 % закрытие) - 2100\n"
        "• Древнее Море (100 % закрытие) 1300\n"
        "• Весь Фонтейн (100 % закрытие) 6400\n"
        "\n🗿 - Натлан\n"
        "• Натлан 5.0 (100 % закрытие) - 3000\n"
        "• Очканатлан (100 % закрытие) - 1800\n"
        "• Натлан 5.5 (100 % закрытие) - 2250 \n"
        "\n❕ Второстепенные услуги\n"
        "• Квест Аранар - 1800\n"
        "• Уход за аккаунтом ( месяц ) - 3000\n"
    ),
    "hsr_price": (
        "Хонкаи Стар Рейл\n"
        "Слава безымянных - 800\n"
        "Честь безымянных - 1600\n"
        "Х300 - 350\n"
        "Х980 - 1380\n"
        "Х1980 - 2150\n"
        "Х3280 - 3510\n"
        "Х6480 - 7050\n"
        "Календарь - 350\n"
    ),
    "zzz_price": (
        "Зенлес Зоне Зиро\n"
        "Фонд Риду продвинутый - 810\n"
        "Фонд Риду премиальный - 1610\n"
        "Х300 - 355\n"
        "Х980 - 1110\n"
        "Х1980 - 2180\n"
        "Х3280 - 3650\n"
        "Х6480 - 7100\n"
        "Набор - 355\n"
    ),
    "roblox_price": (
        "Роблокс\n"
        "Х500 - 470\n"
        "Х1000 - 910\n"
        "Х2000 - 1810\n"
        "Х5250 - 4400\n"
        "Х11000 - 8800\n"
        "Х24000 - 18000\n"
    ),
    "clash_price": (
        "Клеш Рояль\n"
        "Пасс рояль - 94\n"
        "Х500 - 395\n"
        "Х1200 - 795\n"
        "Х2500 - 1590\n"
        "Х6500 - 3985\n"
        "Х14000 - 7995\n"
        "Х80 - 75\n"
    ),
    "brawl_price": (
        "Бравл Старс\n"
        "Бравл Пасс - 500\n"
        "Улучшение до плюс - 315\n"
        "Бравл Пасс плюс - 770\n"
        "Х30 - 155\n"
        "Х80 - 385\n"
        "Х170 - 780\n"
        "Х360 - 1580\n"
        "Х950 - 3900\n"
        "Х2000 - 7800\n"
    ),
}

# --- Кнопки для позиций по платформам ---
PLATFORM_ITEMS = {
    "genshin_price": [
        ("Гимн", 700), ("Хор", 1410), ("Х65", 70), ("Х300", 310), ("Х980", 980), ("Х1980", 1850), ("Х3280", 2900), ("Х6480", 5800), ("Карточка", 310)
    ],
    "genshin_locations": [
        ("Мондштадт (100%)", 850), ("Драконий хребет (100%)", 700), ("Мондштадт/Драконий хребет (100%)", 1300),
        ("Ли Юэ (100%)", 2300), ("Разлом (100%)", 1000), ("Ли Юэ/Разлом (100%)", 3300), ("Долина Чэньюй (100%)", 2200),
        ("Инадзума (100%)", 2000), ("Энканомия (100%)", 1200), ("Инадзума/Энканомия (100%)", 3200),
        ("Сумеру (100%)", 2200), ("Пустыня Колоннад (100%)", 1350), ("Пустыня Хадрамавет (100%)", 1800), ("Царство Фаракхерт (100%)", 1200), ("Все пустыни Сумеру (100%)", 4350), ("Сумеру тропики и пустыня (100%)", 6500),
        ("Кур Де Фонтейн (100%)", 1800), ("Институт Фонтейна (100%)", 1700), ("Лес Эриний (100%)", 2100), ("Древнее Море (100%)", 1300), ("Весь Фонтейн (100%)", 6400),
        ("Натлан 5.0 (100%)", 3000), ("Очканатлан (100%)", 1800), ("Натлан 5.5 (100%)", 2250),
        ("Квест Аранар", 1800), ("Уход за аккаунтом (месяц)", 3000)
    ],
    "hsr_price": [
        ("Слава безымянных", 800), ("Честь безымянных", 1600), ("Х300", 350), ("Х980", 1380), ("Х1980", 2150), ("Х3280", 3510), ("Х6480", 7050), ("Календарь", 350)
    ],
    "zzz_price": [
        ("Фонд Риду продвинутый", 810), ("Фонд Риду премиальный", 1610), ("Х300", 355), ("Х980", 1110), ("Х1980", 2180), ("Х3280", 3650), ("Х6480", 7100), ("Набор", 355)
    ],
    "roblox_price": [
        ("Х500", 470), ("Х1000", 910), ("Х2000", 1810), ("Х5250", 4400), ("Х11000", 8800), ("Х24000", 18000)
    ],
    "clash_price": [
        ("Пасс рояль", 94), ("Х500", 395), ("Х1200", 795), ("Х2500", 1590), ("Х6500", 3985), ("Х14000", 7995), ("Х80", 75)
    ],
    "brawl_price": [
        ("Бравл Пасс", 500), ("Улучшение до плюс", 315), ("Бравл Пасс плюс", 770), ("Х30", 155), ("Х80", 385), ("Х170", 780), ("Х360", 1580), ("Х950", 3900), ("Х2000", 7800)
    ]
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
    return kb

def get_items_keyboard(platform):
    kb = types.InlineKeyboardMarkup()
    for name, price in PLATFORM_ITEMS.get(platform, []):
        kb.add(types.InlineKeyboardButton(text=f"{name} ({price}₽)", callback_data=f"item_{platform}_{name}"))
    return kb

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите платформу для покупки услуги:", reply_markup=get_platforms_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "genshin_price")
def genshin_price_handler(call):
    bot.send_message(call.message.chat.id, "Выберите товар Genshin Impact:", reply_markup=get_items_keyboard("genshin_price"))
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
        bot.send_message(call.message.chat.id, "Выберите товар Genshin Impact:", reply_markup=get_items_keyboard("genshin_price"))
    # Genshin Locations: фото + клавиатура с позициями
    elif call.data == "genshin_locations":
        bot.send_message(call.message.chat.id, "Выберите позицию:", reply_markup=get_items_keyboard("genshin_locations"))
    # Steam: фото + запрос логина
    elif call.data == "steam":
        user_states[call.from_user.id] = {"state": "awaiting_steam_login"}
        bot.send_message(call.message.chat.id, "Пожалуйста, введите ваш логин Steam:")
    # Остальные: фото + клавиатура с позициями
    elif call.data in PLATFORM_ITEMS:
        platform_name = dict(PLATFORMS)[call.data]
        bot.send_message(call.message.chat.id, f"Выберите позицию {platform_name}:", reply_markup=get_items_keyboard(call.data))
    bot.answer_callback_query(call.id)

# Обработка выбора позиции для всех платформ (кроме Steam)
@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def item_selected_handler(call):
    parts = call.data.split("_", 2)
    platform = parts[1]
    name = parts[2]
    price = None
    for n, p in PLATFORM_ITEMS.get(platform, []):
        if n == name:
            price = p
            break
    if price is not None:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Подтвердить заказ", callback_data=f"confirm_{platform}_{name}"))
        bot.send_message(call.message.chat.id, f"Вы выбрали: {name} ({price}₽). Подтвердите заказ:", reply_markup=kb)
    else:
        bot.send_message(call.message.chat.id, "Ошибка выбора позиции. Попробуйте снова.")
    bot.answer_callback_query(call.id)

# Обработка подтверждения заказа по позиции
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_item_handler(call):
    parts = call.data.split("_", 2)
    platform = parts[1]
    name = parts[2] if len(parts) > 2 else None
    username = call.from_user.username or 'Без username'
    if name:
        price = None
        for n, p in PLATFORM_ITEMS.get(platform, []):
            if n == name:
                price = p
                break
        text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {dict(PLATFORMS).get(platform, platform)}\nПозиция: {name} ({price}₽)\nПользователь: @{username} ({call.from_user.id})"
    else:
        text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {dict(PLATFORMS).get(platform, platform)}\nПользователь: @{username} ({call.from_user.id})"
    bot.send_message(MANAGER_CHAT_ID, text)
    bot.send_message(call.message.chat.id, "Спасибо за заказ! С вами свяжется менеджер для оплаты.")
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