import os
import telebot
from telebot import types
from dotenv import load_dotenv
import time
import json

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
    "genshin_price": GENSHIN_ITEMS,
    "steam": [],  # Для Steam отдельная логика
    "hsr_price": [
        ("60 звездного нефрита", 70),
        ("300 звездного нефрита", 310),
        ("980 звездного нефрита", 980),
        ("1980 звездного нефрита", 1850),
        ("3280 звездного нефрита", 2900),
        ("6480 звездного нефрита", 5800),
        ("Пакет экспресс-пасс", 310)
    ],
    "zzz_price": [
        ("60 полярных кристаллов", 70),
        ("300 полярных кристаллов", 310),
        ("980 полярных кристаллов", 980),
        ("1980 полярных кристаллов", 1850),
        ("3280 полярных кристаллов", 2900),
        ("6480 полярных кристаллов", 5800),
        ("Пакет экспресс-пасс", 310)
    ],
    "roblox_price": [
        ("80 Robux", 100),
        ("400 Robux", 500),
        ("800 Robux", 1000),
        ("1700 Robux", 2000)
    ],
    "clash_price": [
        ("80 гемов", 100),
        ("500 гемов", 500),
        ("1200 гемов", 1000),
        ("2500 гемов", 2000)
    ],
    "brawl_price": [
        ("30 гемов", 100),
        ("80 гемов", 250),
        ("170 гемов", 500),
        ("360 гемов", 1000),
        ("950 гемов", 2500),
        ("2000 гемов", 5000)
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
        ("Мондштадт (100%)", 850),
        ("Драконий хребет (100%)", 700),
        ("Мондштадт + Драконий хребет (100%)", 1300)
    ],
    "liyue": [
        ("Ли Юэ (100%)", 2300),
        ("Разлом (100%)", 1000),
        ("Ли Юэ + Разлом (100%)", 3300),
        ("Долина Чэньюй (100%)", 2200)
    ],
    "inazuma": [
        ("Инадзума (100%)", 2000),
        ("Энканомия (100%)", 1200),
        ("Инадзума + Энканомия (100%)", 3200)
    ],
    "sumeru": [
        ("Сумеру (100%)", 2200),
        ("Пустыня Колоннад (100%)", 1350),
        ("Пустыня Хадрамавет (100%)", 1800),
        ("Царство Фаракхерт (100%)", 1200),
        ("Все пустыни Сумеру (100%)", 4350),
        ("Сумеру (тропики + пустыня) (100%)", 6500)
    ],
    "fontaine": [
        ("Кур Де Фонтейн (100%)", 1800),
        ("Институт Фонтейна (100%)", 1700),
        ("Лес Эриний (100%)", 2100),
        ("Древнее Море (100%)", 1300),
        ("Весь Фонтейн (100%)", 6400)
    ],
    "natlan": [
        ("Натлан 5.0 (100%)", 3000),
        ("Очканатлан (100%)", 1800),
        ("Натлан 5.5 (100%)", 2250)
    ],
    "other_services": [
        ("Квест Аранар", 1800),
        ("Уход за аккаунтом (месяц)", 3000)
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
ADMIN_IDS = [526427613, 5174082916]  # Пример, замените на реальные Telegram user_id

# --- Для хранения изменённых цен (в памяти) ---
MODIFIED_PRICES = {}

# --- Вспомогательные функции ---
def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_price(platform, idx, region_code=None):
    if platform == 'genshin_locations' and region_code is not None:
        key = f"{region_code}_{idx}"
        return MODIFIED_PRICES.get(key) or LOCATION_ITEMS[region_code][idx][1]
    else:
        key = f"{platform}_{idx}"
        return MODIFIED_PRICES.get(key) or PLATFORM_ITEMS[platform][idx][1]

def set_price(platform, idx, new_price, region_code=None):
    if platform == 'genshin_locations' and region_code is not None:
        key = f"{region_code}_{idx}"
        MODIFIED_PRICES[key] = new_price
    else:
        key = f"{platform}_{idx}"
        MODIFIED_PRICES[key] = new_price
    save_prices()

# --- FSM для смены цены ---
price_change_state = {}

@bot.message_handler(commands=['setprice'])
def setprice_start(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа.")
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for callback, name in PLATFORMS:
        kb.add(types.KeyboardButton(name))
    bot.send_message(message.chat.id, "Выберите платформу:", reply_markup=kb)
    price_change_state[message.from_user.id] = {'step': 'platform'}

@bot.message_handler(func=lambda m: price_change_state.get(m.from_user.id, {}).get('step') == 'platform')
def setprice_choose_platform(message):
    platform = None
    for code, name in PLATFORMS:
        if message.text == name:
            platform = code
            break
    if not platform:
        bot.reply_to(message, "Платформа не найдена. Попробуйте снова.")
        return
    price_change_state[message.from_user.id] = {'step': 'item', 'platform': platform}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if platform == 'genshin_locations':
        for region_code, region_name in LOCATION_REGIONS.items():
            kb.add(types.KeyboardButton(region_name))
        bot.send_message(message.chat.id, "Выберите регион:", reply_markup=kb)
    else:
        for idx, (name, price) in enumerate(PLATFORM_ITEMS[platform]):
            kb.add(types.KeyboardButton(f"{name} ({get_price(platform, idx)}₽)"))
        bot.send_message(message.chat.id, "Выберите позицию:", reply_markup=kb)

@bot.message_handler(func=lambda m: price_change_state.get(m.from_user.id, {}).get('step') == 'item')
def setprice_choose_item(message):
    state = price_change_state[message.from_user.id]
    platform = state['platform']
    if platform == 'genshin_locations':
        region_code = None
        for code, name in LOCATION_REGIONS.items():
            if message.text == name:
                region_code = code
                break
        if not region_code:
            bot.reply_to(message, "Регион не найден. Попробуйте снова.")
            return
        price_change_state[message.from_user.id] = {'step': 'loc_item', 'platform': platform, 'region_code': region_code}
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for idx, (name, price) in enumerate(LOCATION_ITEMS[region_code]):
            kb.add(types.KeyboardButton(f"{name} ({get_price(platform, idx, region_code)}₽)"))
        bot.send_message(message.chat.id, "Выберите позицию:", reply_markup=kb)
    else:
        idx = None
        for i, (name, price) in enumerate(PLATFORM_ITEMS[platform]):
            if message.text.startswith(name):
                idx = i
                break
        if idx is None:
            bot.reply_to(message, "Позиция не найдена. Попробуйте снова.")
            return
        price_change_state[message.from_user.id] = {'step': 'new_price', 'platform': platform, 'idx': idx}
        bot.send_message(message.chat.id, "Введите новую цену:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: price_change_state.get(m.from_user.id, {}).get('step') == 'loc_item')
def setprice_choose_loc_item(message):
    state = price_change_state[message.from_user.id]
    region_code = state['region_code']
    idx = None
    for i, (name, price) in enumerate(LOCATION_ITEMS[region_code]):
        if message.text.startswith(name):
            idx = i
            break
    if idx is None:
        bot.reply_to(message, "Позиция не найдена. Попробуйте снова.")
        return
    price_change_state[message.from_user.id] = {'step': 'new_price', 'platform': 'genshin_locations', 'region_code': region_code, 'idx': idx}
    bot.send_message(message.chat.id, "Введите новую цену:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: price_change_state.get(m.from_user.id, {}).get('step') == 'new_price')
def setprice_set_new_price(message):
    state = price_change_state[message.from_user.id]
    try:
        new_price = int(message.text.strip())
        if new_price <= 0:
            raise ValueError
    except:
        bot.reply_to(message, "Введите корректную цену (целое число > 0)")
        return
    platform = state['platform']
    idx = state['idx']
    region_code = state.get('region_code')
    set_price(platform, idx, new_price, region_code)
    bot.send_message(message.chat.id, f"Цена успешно изменена!", reply_markup=types.ReplyKeyboardRemove())
    price_change_state.pop(message.from_user.id, None)

# --- Команда рассылки ---
broadcast_state = {}
ALL_USERS = set()  # Для хранения user_id всех пользователей, которые писали боту

@bot.message_handler(commands=['broadcast'])
def broadcast_start(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа.")
        return
    bot.send_message(message.chat.id, "Введите текст рассылки:")
    broadcast_state[message.from_user.id] = True

@bot.message_handler(func=lambda m: broadcast_state.get(m.from_user.id))
def broadcast_send(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа.")
        broadcast_state.pop(message.from_user.id, None)
        return
    text = message.text
    count = 0
    for user_id in ALL_USERS:
        try:
            bot.send_message(user_id, text)
            count += 1
        except:
            pass
    bot.send_message(message.chat.id, f"Рассылка завершена. Отправлено: {count}")
    broadcast_state.pop(message.from_user.id, None)

# --- Сбор user_id для рассылки ---
@bot.message_handler(func=lambda m: True)
def collect_user(message):
    ALL_USERS.add(message.from_user.id)
    save_users()

def clean_previous_messages(chat_id):
    """Удаляет все предыдущие сообщения бота в чате"""
    if chat_id in messages_to_delete:
        for msg_id in messages_to_delete[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
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
    for idx, (name, value) in enumerate(items):
        if isinstance(value, int):
            key = f"{platform}_{idx}"
            callback_data = f"item|||{key}"
            kb.add(types.InlineKeyboardButton(text=f"{name} ({value}₽)", callback_data=callback_data))
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
    # Добавляю кнопку назад в главное меню
    kb.add(types.InlineKeyboardButton(
        text="◀️ В главное меню",
        callback_data="back_to_platforms"
    ))
    return kb

@bot.message_handler(commands=['start'])
def start_handler(message):
    clean_previous_messages(message.chat.id)
    user_states.pop(message.from_user.id, None)
    msg = bot.send_message(
        message.chat.id,
        "Добро пожаловать! Выберите платформу для покупки услуги:",
        reply_markup=get_platforms_keyboard()
    )
    add_message_to_delete(message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data in PLATFORM_PHOTOS)
def platform_handler(call):
    clean_previous_messages(call.message.chat.id)
    platform = call.data
    
    # Отправляем фото прайса
    photo_info = PLATFORM_PHOTOS.get(platform)
    if photo_info:
        filename, caption = photo_info
        try:
            with open(filename, "rb") as photo:
                photo_msg = bot.send_photo(call.message.chat.id, photo, caption=caption)
                add_message_to_delete(call.message.chat.id, photo_msg.message_id)
        except Exception as e:
            error_msg = bot.send_message(call.message.chat.id, f"Не удалось отправить фото прайса. Обратитесь к менеджеру.")
            add_message_to_delete(call.message.chat.id, error_msg.message_id)
    
    if platform == "genshin_locations":
        msg = bot.send_message(
            call.message.chat.id,
            "💎 Закрытие локаций в Genshin Impact\nВыберите регион:",
            reply_markup=get_locations_keyboard()
        )
        add_message_to_delete(call.message.chat.id, msg.message_id)
    elif platform == "steam":
        user_states[call.from_user.id] = {"state": "awaiting_steam_login"}
        msg = bot.send_message(call.message.chat.id, "Пожалуйста, введите ваш логин Steam:")
        add_message_to_delete(call.message.chat.id, msg.message_id)
    else:
        platform_name = dict(PLATFORMS)[platform]
        msg = bot.send_message(
            call.message.chat.id,
            f"Выберите позицию {platform_name}:",
            reply_markup=get_items_keyboard(platform)
        )
        add_message_to_delete(call.message.chat.id, msg.message_id)
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("genshin_loc|||"))
def genshin_location_handler(call):
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
    clean_previous_messages(call.message.chat.id)
    key = call.data.split("|||")[1]
    print(f"[DEBUG] Выбран ключ товара: {key}")
    # Проверяем, к какой категории относится ключ
    if key in LOCATION_ITEM_KEYS:
        region_code, name, price = LOCATION_ITEM_KEYS[key]
        platform = "genshin_locations"
    elif key in PLATFORM_ITEM_KEYS:
        platform, name, price = PLATFORM_ITEM_KEYS[key]
    else:
        print(f"[DEBUG] Неизвестный ключ товара: {key}")
        bot.answer_callback_query(call.id, "Товар не найден")
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        text="✅ Подтвердить заказ",
        callback_data=f"confirm|||{key}"
    ))
    # Кнопка назад
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
    clean_previous_messages(call.message.chat.id)
    key = call.data.split("|||")[1]
    # Проверяем, к какой категории относится ключ
    if key in LOCATION_ITEM_KEYS:
        region_code, name, price = LOCATION_ITEM_KEYS[key]
        platform = "genshin_locations"
    elif key in PLATFORM_ITEM_KEYS:
        platform, name, price = PLATFORM_ITEM_KEYS[key]
    else:
        bot.answer_callback_query(call.id, "Ошибка при подтверждении заказа")
        return
    username = call.from_user.username or 'Без username'
    platform_name = dict(PLATFORMS).get(platform, platform)
    # Отправляем уведомление менеджеру
    text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {platform_name}\nПозиция: {name} ({price}₽)\nПользователь: @{username} ({call.from_user.id})"
    bot.send_message(MANAGER_CHAT_ID, text)
    # Отправляем подтверждение пользователю
    msg = bot.send_message(
        call.message.chat.id,
        f"✅ Заказ подтвержден!\n\n{name} ({price}₽)\n\nС вами свяжется менеджер для оплаты."
    )
    add_message_to_delete(call.message.chat.id, msg.message_id)

# Остальные обработчики для Steam (оставлены без изменений)
@bot.callback_query_handler(func=lambda call: call.data == "steam")
def back_to_steam_handler(call):
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
def save_prices():
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(MODIFIED_PRICES, f, ensure_ascii=False)

def load_prices():
    global MODIFIED_PRICES
    try:
        with open(PRICES_FILE, 'r', encoding='utf-8') as f:
            MODIFIED_PRICES = json.load(f)
    except Exception:
        MODIFIED_PRICES = {}

# --- Функции для сохранения/загрузки пользователей ---
def save_users():
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(ALL_USERS), f)

def load_users():
    global ALL_USERS
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            ALL_USERS = set(json.load(f))
    except Exception:
        ALL_USERS = set()

# --- Загружаем цены и пользователей при старте ---
load_prices()
load_users()

if __name__ == '__main__':
    bot.polling(none_stop=True)
