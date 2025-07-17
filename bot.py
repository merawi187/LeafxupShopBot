import os
import telebot
from telebot import types
from dotenv import load_dotenv
import time
import json
import sqlite3

DB_FILE = 'data.db'

PRICES_FILE = 'prices.json'
USERS_FILE = 'users.json'

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

# Добавляю определение PLATFORM_ITEMS для всех платформ, кроме genshin_locations
PLATFORM_ITEMS = {
    "genshin_price": [
        ("Гимн", 700), ("Хор", 1410), ("Х65", 70), ("Х300", 310), ("Х980", 980), ("Х1980", 1850), ("Х3280", 2900), ("Х6480", 5800), ("Карточка", 310)
    ],
    "steam": [],
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
messages_to_delete = {}  # Для хранения ID сообщений, которые нужно удалить

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

# Полностью переработанный раздел локаций Genshin Impact
LOCATION_REGIONS = {
    "mondstadt": "🌪 Мондштадт",
    "liyue": "🪨 Ли Юэ",
    "inazuma": "⚡️ Инадзума",
    "sumeru": "🌿 Сумеру",
    "fontaine": "🫵 Фонтейн",
    "natlan": "🗿 Натлан",
    "other_services": "❕ Доп. услуги"
}

LOCATION_ITEMS = {
    "mondstadt": [
        ("Мондштадт (100%)", 850), ("Драконий хребет (100%)", 700), ("Мондштадт/Драконий хребет (100%)", 1300)
    ],
    "liyue": [
        ("Ли Юэ (100%)", 2300), ("Разлом (100%)", 1000), ("Ли Юэ/Разлом (100%)", 3300), ("Долина Чэньюй (100%)", 2200)
    ],
    "inazuma": [
        ("Инадзума (100%)", 2000), ("Энканомия (100%)", 1200), ("Инадзума/Энканомия (100%)", 3200)
    ],
    "sumeru": [
        ("Сумеру (100%)", 2200), ("Пустыня Колоннад (100%)", 1350), ("Пустыня Хадрамавет (100%)", 1800), ("Царство Фаракхерт (100%)", 1200), ("Все пустыни Сумеру (100%)", 4350), ("Сумеру тропики и пустыня (100%)", 6500)
    ],
    "fontaine": [
        ("Кур Де Фонтейн (100%)", 1800), ("Институт Фонтейна (100%)", 1700), ("Лес Эриний (100%)", 2100), ("Древнее Море (100%)", 1300), ("Весь Фонтейн (100%)", 6400)
    ],
    "natlan": [
        ("Натлан 5.0 (100%)", 3000), ("Очканатлан (100%)", 1800), ("Натлан 5.5 (100%)", 2250)
    ],
    "other_services": [
        ("Квест Аранар", 1800), ("Уход за аккаунтом (месяц)", 3000)
    ]
}

# --- Маппинг для коротких callback_data ---
# Для Genshin Impact (закрытие локаций)
LOCATION_ITEM_KEYS = {}
for region_code, items in LOCATION_ITEMS.items():
    for idx, (name, price) in enumerate(items):
        key = f"{region_code}_{idx}"
        LOCATION_ITEM_KEYS[key] = (region_code, name, price)

# Для остальных платформ
PLATFORM_ITEM_KEYS = {}
for platform, items in PLATFORM_ITEMS.items():
    for idx, (name, price) in enumerate(items):
        key = f"{platform}_{idx}"
        PLATFORM_ITEM_KEYS[key] = (platform, name, price)

# --- Админские ID (замените на свои) ---
ADMIN_IDS = [526427613, 5174082916]

# --- Для хранения изменённых цен (в памяти) ---
MODIFIED_PRICES = {}

# --- Инициализация базы данных ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    c.execute('''CREATE TABLE IF NOT EXISTS prices (
        key TEXT PRIMARY KEY,
        price INTEGER
    )''')
    conn.commit()
    conn.close()

init_db()

# --- Работа с пользователями ---
def add_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

# --- Работа с ценами ---
# Удаляю функции set_price_db, get_price_db, set_price, get_price, price_change_state и все message_handler с setprice

# --- Команда рассылки ---
broadcast_state = {}

@bot.message_handler(commands=['broadcast'])
def broadcast_start(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Нет доступа.")
        return
    clean_previous_messages(message.chat.id)
    bot.send_message(message.chat.id, "Введите текст рассылки:")
    broadcast_state[message.from_user.id] = True

@bot.message_handler(func=lambda m: broadcast_state.get(m.from_user.id))
def broadcast_send(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Нет доступа.")
        broadcast_state.pop(message.from_user.id, None)
        return
    text = message.text
    count = 0
    for user_id in get_all_users():
        try:
            bot.send_message(user_id, text)
            count += 1
        except Exception as e:
            pass
    bot.send_message(message.chat.id, f"Рассылка завершена. Отправлено: {count}")
    broadcast_state.pop(message.from_user.id, None)

# --- Сбор user_id для рассылки ---
# Удалён обработчик catch-all callback_query_handler и функция collect_user_callback

def clean_previous_messages(chat_id):
    """Удаляет все предыдущие сообщения бота в чате"""
    if chat_id in messages_to_delete:
        for msg_id in messages_to_delete[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                pass
        messages_to_delete[chat_id] = []

def add_message_to_delete(chat_id, message_id):
    """Добавляет сообщение в список для удаления"""
    if chat_id not in messages_to_delete:
        messages_to_delete[chat_id] = []
    messages_to_delete[chat_id].append(message_id)

def get_platforms_keyboard():
    kb = types.InlineKeyboardMarkup()
    for callback, name in PLATFORMS:
        kb.add(types.InlineKeyboardButton(text=name, callback_data=callback))
    return kb

def get_items_keyboard(platform):
    kb = types.InlineKeyboardMarkup()
    items = PLATFORM_ITEMS.get(platform, [])
    if not items:
        kb.add(types.InlineKeyboardButton(text="Нет доступных товаров", callback_data="none"))
        kb.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_platforms"))
        return kb
    for idx, (name, price) in enumerate(items):
        key = f"{platform}_{idx}"
        callback_data = f"item|||{key}"
        kb.add(types.InlineKeyboardButton(text=f"{name} ({price}₽)", callback_data=callback_data))
    kb.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_platforms"))
    return kb

def get_locations_keyboard():
    """Клавиатура для выбора региона"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    for region_code, region_name in LOCATION_REGIONS.items():
        kb.add(types.InlineKeyboardButton(
            text=region_name,
            callback_data=f"genshin_loc|||{region_code}"
        ))
    # Добавляю кнопку назад в главное меню
    kb.add(types.InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_platforms"))
    return kb

def get_location_items_keyboard(region_code):
    """Клавиатура с товарами для конкретного региона"""
    kb = types.InlineKeyboardMarkup()
    items = LOCATION_ITEMS.get(region_code, [])
    for idx, (name, price) in enumerate(items):
        key = f"{region_code}_{idx}"
        kb.add(types.InlineKeyboardButton(
            text=f"{name} - {price}₽",
            callback_data=f"item|||{key}"
        ))
    kb.add(types.InlineKeyboardButton(
        text="◀️ Назад к регионам",
        callback_data="genshin_locations"
    ))
    kb.add(types.InlineKeyboardButton(
        text="◀️ В главное меню",
        callback_data="back_to_platforms"
    ))
    return kb

@bot.message_handler(commands=['start'])
def start_handler(message):
    clean_previous_messages(message.chat.id)
    add_user(message.from_user.id)
    user_states.pop(message.from_user.id, None)
    msg = bot.send_message(
        message.chat.id,
        "Добро пожаловать! Выберите платформу для покупки услуги:",
        reply_markup=get_platforms_keyboard()
    )
    add_message_to_delete(message.chat.id, msg.message_id)

def is_admin(user_id):
    return user_id in ADMIN_IDS

@bot.message_handler(commands=['users'])
def show_users(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа.")
        return
    users = get_all_users()
    if not users:
        bot.send_message(message.chat.id, "Список пользователей пуст.")
        return
    text = 'Пользователи (user_id):\n' + '\n'.join(str(u) for u in users)
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['adduser'])
def add_user_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа.")
        return
    try:
        user_id = int(message.text.split()[1])
        add_user(user_id)
        bot.send_message(message.chat.id, f"Пользователь {user_id} добавлен.")
    except Exception:
        bot.send_message(message.chat.id, "Используйте: /adduser <user_id>")

@bot.message_handler(commands=['deluser'])
def del_user_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа.")
        return
    try:
        user_id = int(message.text.split()[1])
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"Пользователь {user_id} удалён.")
    except Exception:
        bot.send_message(message.chat.id, "Используйте: /deluser <user_id>")

# Исправляю отображение кнопок под фото и удаление сообщений
@bot.callback_query_handler(func=lambda call: call.data in PLATFORM_PHOTOS)
def platform_handler(call):
    add_user(call.from_user.id)
    clean_previous_messages(call.message.chat.id)
    platform = call.data
    photo_info = PLATFORM_PHOTOS.get(platform)
    if platform == "steam":
        user_states[call.from_user.id] = {"state": "awaiting_steam_login"}
        msg = bot.send_message(call.message.chat.id, "Пожалуйста, введите ваш логин Steam:")
        add_message_to_delete(call.message.chat.id, msg.message_id)
    elif photo_info:
        filename, caption = photo_info
        try:
            with open(filename, "rb") as photo:
                # Для genshin_locations — отдельная клавиатура, для остальных — get_items_keyboard
                if platform == "genshin_locations":
                    reply_markup = get_locations_keyboard()
                else:
                    reply_markup = get_items_keyboard(platform)
                msg = bot.send_photo(call.message.chat.id, photo, caption=caption, reply_markup=reply_markup)
                add_message_to_delete(call.message.chat.id, msg.message_id)
        except Exception as e:
            error_msg = bot.send_message(call.message.chat.id, f"Не удалось отправить фото прайса. Обратитесь к менеджеру. ({e})")
            add_message_to_delete(call.message.chat.id, error_msg.message_id)
    else:
        msg = bot.send_message(
            call.message.chat.id,
            f"Выберите позицию {dict(PLATFORMS)[platform]}:",
            reply_markup=get_items_keyboard(platform)
        )
        add_message_to_delete(call.message.chat.id, msg.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("genshin_loc|||"))
def genshin_location_handler(call):
    add_user(call.from_user.id)
    clean_previous_messages(call.message.chat.id)
    region_code = call.data.split("|||")[1]
    print(f"[DEBUG] Выбран регион: {region_code}")
    if region_code in LOCATION_REGIONS:
        region_name = LOCATION_REGIONS[region_code]
        msg = bot.send_message(
            call.message.chat.id,
            f"💎 {region_name} - доступные услуги:",
            reply_markup=get_location_items_keyboard(region_code)
        )
        add_message_to_delete(call.message.chat.id, msg.message_id)
    else:
        print(f"[DEBUG] Неизвестный регион: {region_code}")
        bot.answer_callback_query(call.id, "Регион не найден")

@bot.callback_query_handler(func=lambda call: call.data == "genshin_locations")
def back_to_locations_handler(call):
    add_user(call.from_user.id)
    clean_previous_messages(call.message.chat.id)
    msg = bot.send_message(
        call.message.chat.id,
        "💎 Закрытие локаций в Genshin Impact\nВыберите регион:",
        reply_markup=get_locations_keyboard()
    )
    add_message_to_delete(call.message.chat.id, msg.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_platforms")
def back_to_platforms_handler(call):
    add_user(call.from_user.id)
    clean_previous_messages(call.message.chat.id)
    msg = bot.send_message(
        call.message.chat.id,
        "Добро пожаловать! Выберите платформу для покупки услуги:",
        reply_markup=get_platforms_keyboard()
    )
    add_message_to_delete(call.message.chat.id, msg.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("item|||"))
def item_selected_handler(call):
    add_user(call.from_user.id)
    clean_previous_messages(call.message.chat.id)
    key = call.data.split("|||")[1]
    if key in LOCATION_ITEM_KEYS:
        region_code, name, _ = LOCATION_ITEM_KEYS[key]
        platform = "genshin_locations"
        try:
            idx = int(key.split('_')[1])
            items = LOCATION_ITEMS[region_code]
            if idx < 0 or idx >= len(items):
                raise IndexError
        except (IndexError, ValueError, KeyError):
            bot.answer_callback_query(call.id, "Ошибка позиции")
            return
        price = items[idx][1] # Возвращаю цену напрямую
    elif key in PLATFORM_ITEM_KEYS:
        platform, name, _ = PLATFORM_ITEM_KEYS[key]
        try:
            idx = int(key.split('_')[1])
            items = PLATFORM_ITEMS[platform]
            if idx < 0 or idx >= len(items):
                raise IndexError
        except (IndexError, ValueError, KeyError):
            bot.answer_callback_query(call.id, "Ошибка позиции")
            return
        price = items[idx][1] # Возвращаю цену напрямую
    else:
        bot.answer_callback_query(call.id, "Товар не найден")
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        text="✅ Подтвердить заказ",
        callback_data=f"confirm|||{key}"
    ))
    if platform == "genshin_locations":
        kb.add(types.InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"genshin_loc|||{region_code}"
        ))
        kb.add(types.InlineKeyboardButton(
            text="◀️ В главное меню",
            callback_data="back_to_platforms"
        ))
    else:
        kb.add(types.InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=platform
        ))
    msg = bot.send_message(
        call.message.chat.id,
        f"Вы выбрали: {name} ({price}₽)\n\nПодтвердите заказ:",
        reply_markup=kb
    )
    add_message_to_delete(call.message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm|||"))
def confirm_order_handler(call):
    add_user(call.from_user.id)
    clean_previous_messages(call.message.chat.id)
    key = call.data.split("|||")[1]
    if key in LOCATION_ITEM_KEYS:
        region_code, name, _ = LOCATION_ITEM_KEYS[key]
        platform = "genshin_locations"
        try:
            idx = int(key.split('_')[1])
            items = LOCATION_ITEMS[region_code]
            if idx < 0 or idx >= len(items):
                raise IndexError
        except (IndexError, ValueError, KeyError):
            bot.answer_callback_query(call.id, "Ошибка позиции")
            return
        price = items[idx][1] # Возвращаю цену напрямую
    elif key in PLATFORM_ITEM_KEYS:
        platform, name, _ = PLATFORM_ITEM_KEYS[key]
        try:
            idx = int(key.split('_')[1])
            items = PLATFORM_ITEMS[platform]
            if idx < 0 or idx >= len(items):
                raise IndexError
        except (IndexError, ValueError, KeyError):
            bot.answer_callback_query(call.id, "Ошибка позиции")
            return
        price = items[idx][1] # Возвращаю цену напрямую
    else:
        bot.answer_callback_query(call.id, "Ошибка при подтверждении заказа")
        return
    username = call.from_user.username or 'Без username'
    platform_name = dict(PLATFORMS).get(platform, platform)
    text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {platform_name}\nПозиция: {name} ({price}₽)\nПользователь: @{username} ({call.from_user.id})"
    bot.send_message(MANAGER_CHAT_ID, text)
    msg = bot.send_message(
        call.message.chat.id,
        f"✅ Заказ подтвержден!\n\n{name} ({price}₽)\n\nС вами свяжется менеджер для оплаты."
    )
    add_message_to_delete(call.message.chat.id, msg.message_id)

# Остальные обработчики для Steam (оставлены без изменений)
@bot.callback_query_handler(func=lambda call: call.data == "steam")
def back_to_steam_handler(call):
    add_user(call.from_user.id)
    try:
        user_states.pop(call.from_user.id, None)
        clean_previous_messages(call.message.chat.id)
        platform_handler(call)
    except Exception as e:
        print(f"Error in back_to_steam_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка возврата. Попробуйте снова.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "awaiting_steam_login")
def steam_login_handler(message):
    clean_previous_messages(message.chat.id)
    login = message.text.strip()
    user_states[message.from_user.id] = {"state": "awaiting_steam_amount", "login": login}
    msg = bot.send_message(message.chat.id, "Введите сумму пополнения в рублях (от 100 до 25000):")
    add_message_to_delete(message.chat.id, msg.message_id)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "awaiting_steam_amount")
def steam_amount_handler(message):
    clean_previous_messages(message.chat.id)
    try:
        amount = float(message.text.strip().replace(',', '.'))
        if amount < 100 or amount > 25000:
            msg = bot.send_message(message.chat.id, "Сумма должна быть от 100 до 25000 рублей. Попробуйте снова.")
            add_message_to_delete(message.chat.id, msg.message_id)
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
        kb.add(types.InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_steam"))
        kb.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="steam"))
        
        msg = bot.send_message(
            message.chat.id,
            f"Логин: {login}\nСумма пополнения: {amount}₽\nКомиссия (8%): {commission}₽\nИтого к оплате: {total}₽\n\nПодтвердить заказ?",
            reply_markup=kb
        )
        add_message_to_delete(message.chat.id, msg.message_id)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите корректную сумму в рублях.")
        add_message_to_delete(message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_steam")
def confirm_steam_handler(call):
    add_user(call.from_user.id)
    clean_previous_messages(call.message.chat.id)
    try:
        data = user_states.get(call.from_user.id, {})
        login = data.get("login")
        amount = data.get("amount")
        commission = data.get("commission")
        total = data.get("total")
        username = call.from_user.username or 'Без username'
        
        # Отправляем уведомление менеджеру
        text = f"[НОВЫЙ ЗАКАЗ]\nSteam\nЛогин: {login}\nСумма: {amount}₽\nКомиссия: {commission}₽\nИтого: {total}₽\nПользователь: @{username} ({call.from_user.id})"
        bot.send_message(MANAGER_CHAT_ID, text)
        
        # Отправляем подтверждение пользователю
        msg = bot.send_message(
            call.message.chat.id,
            f"✅ Заказ подтвержден!\n\nЛогин: {login}\nСумма: {amount}₽\nИтого: {total}₽\n\nС вами свяжется менеджер для оплаты."
        )
        add_message_to_delete(call.message.chat.id, msg.message_id)
        
        user_states.pop(call.from_user.id, None)
    except Exception as e:
        print(f"Error in confirm_steam_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка при подтверждении заказа")

# --- Функции для сохранения/загрузки цен ---
# Удаляю функции save_prices, load_prices и все обращения к ним

# --- Функции для сохранения/загрузки пользователей ---
# Удаляю функции save_users, load_users и все обращения к ним

# --- Загружаем цены и пользователей при старте ---
# Удаляю функции load_prices, load_users и все обращения к ним

if __name__ == '__main__':
    bot.polling(none_stop=True)
