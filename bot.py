import os
import telebot
from telebot import types
from dotenv import load_dotenv
import threading
from flask import Flask
import time

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
    "genshin_locations": "💎 Закрытие локаций в Genshin Impact\nВыберите регион:",
    "hsr_price": (
        "Хонкаи Стар Рейл\n"
        "Слава безымянных - 800\n"
        "Честь безымянных - 1600\n"
        "Х300 - 350\n"
        "Х980 - 1380\n"
        "Х1980 - 2150\n"
        "Х3280 - 3510\n"
        "Х6480 - 7050\n"
        "Календарь - 350"
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
        "Набор - 355"
    ),
    "roblox_price": (
        "Роблокс\n"
        "Х500 - 470\n"
        "Х1000 - 910\n"
        "Х2000 - 1810\n"
        "Х5250 - 4400\n"
        "Х11000 - 8800\n"
        "Х24000 - 18000"
    ),
    "clash_price": (
        "Клеш Рояль\n"
        "Пасс рояль - 94\n"
        "Х500 - 395\n"
        "Х1200 - 795\n"
        "Х2500 - 1590\n"
        "Х6500 - 3985\n"
        "Х14000 - 7995\n"
        "Х80 - 75"
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
        "Х2000 - 7800"
    ),
}

PLATFORM_ITEMS = {
    "genshin_price": [
        ("Гимн", 700), ("Хор", 1410), ("Х65", 70), ("Х300", 310),
        ("Х980", 980), ("Х1980", 1850), ("Х3280", 2900), ("Х6480", 5800),
        ("Карточка", 310)
    ],
    "genshin_locations": [
        ("🌪 Мондштадт", "mondstadt"),
        ("🪨 Ли Юэ", "liyue"),
        ("⚡️ Инадзума", "inazuma"),
        ("🌿 Сумеру", "sumeru"),
        ("🫵 Фонтейн", "fontaine"),
        ("🗿 Натлан", "natlan"),
        ("❕ Доп. услуги", "other_services")
    ],
    "hsr_price": [
        ("Слава безымянных", 800), ("Честь безымянных", 1600),
        ("Х300", 350), ("Х980", 1380), ("Х1980", 2150),
        ("Х3280", 3510), ("Х6480", 7050), ("Календарь", 350)
    ],
    "zzz_price": [
        ("Фонд Риду продвинутый", 810), ("Фонд Риду премиальный", 1610),
        ("Х300", 355), ("Х980", 1110), ("Х1980", 2180),
        ("Х3280", 3650), ("Х6480", 7100), ("Набор", 355)
    ],
    "roblox_price": [
        ("Х500", 470), ("Х1000", 910), ("Х2000", 1810),
        ("Х5250", 4400), ("Х11000", 8800), ("Х24000", 18000)
    ],
    "clash_price": [
        ("Пасс рояль", 94), ("Х500", 395), ("Х1200", 795),
        ("Х2500", 1590), ("Х6500", 3985), ("Х14000", 7995), ("Х80", 75)
    ],
    "brawl_price": [
        ("Бравл Пасс", 500), ("Улучшение до плюс", 315),
        ("Бравл Пасс плюс", 770), ("Х30", 155), ("Х80", 385),
        ("Х170", 780), ("Х360", 1580), ("Х950", 3900), ("Х2000", 7800)
    ]
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

def get_platforms_keyboard():
    kb = types.InlineKeyboardMarkup()
    for callback, name in PLATFORMS:
        kb.add(types.InlineKeyboardButton(text=name, callback_data=callback))
    return kb

def get_items_keyboard(platform):
    kb = types.InlineKeyboardMarkup()
    items = PLATFORM_ITEMS.get(platform, [])
    
    for name, value in items:
        if isinstance(value, int):
            callback_data = f"item|||{platform}|||{name}"
            kb.add(types.InlineKeyboardButton(text=f"{name} ({value}₽)", callback_data=callback_data))
        else:
            callback_data = f"genshin_loc|||{value}"
            kb.add(types.InlineKeyboardButton(text=name, callback_data=callback_data))
    
    if platform != "genshin_locations":
        kb.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_platforms"))
    
    return kb

def get_locations_keyboard(region=None):
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    if region is None:
        for name, callback in PLATFORM_ITEMS["genshin_locations"]:
            kb.add(types.InlineKeyboardButton(text=name, callback_data=f"genshin_loc|||{callback}"))
    else:
        items = LOCATION_ITEMS.get(region, [])
        for name, price in items:
            callback_data = f"item|||genshin_locations|||{name}"
            kb.add(types.InlineKeyboardButton(text=f"{name} - {price}₽", callback_data=callback_data))
        
        kb.add(types.InlineKeyboardButton(text="◀️ Назад к регионам", callback_data="genshin_locations"))
    
    return kb

def get_region_by_name(name):
    for region, items in LOCATION_ITEMS.items():
        for item_name, _ in items:
            if item_name == name:
                return region
    return None

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите платформу для покупки услуги:", reply_markup=get_platforms_keyboard())

@bot.callback_query_handler(func=lambda call: call.data in PLATFORM_PHOTOS)
def platform_handler(call):
    platform = call.data
    
    if platform == "genshin_locations":
        bot.send_message(call.message.chat.id, PLATFORM_TEXTS["genshin_locations"], 
                         reply_markup=get_locations_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    photo_info = PLATFORM_PHOTOS.get(platform)
    if photo_info:
        filename, caption = photo_info
        try:
            with open(filename, "rb") as photo:
                bot.send_photo(call.message.chat.id, photo, caption=caption)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Не удалось отправить фото прайса для {caption}. Обратитесь к менеджеру.")
    
    if platform == "steam":
        user_states[call.from_user.id] = {"state": "awaiting_steam_login"}
        bot.send_message(call.message.chat.id, "Пожалуйста, введите ваш логин Steam:")
    else:
        platform_name = dict(PLATFORMS)[platform]
        time.sleep(0.5)
        bot.send_message(call.message.chat.id, f"Выберите позицию {platform_name}:", 
                         reply_markup=get_items_keyboard(platform))
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("genshin_loc|||"))
def genshin_location_handler(call):
    try:
        region = call.data.split("|||")[1]
        region_name = {
            "mondstadt": "🌪 Мондштадт",
            "liyue": "🪨 Ли Юэ",
            "inazuma": "⚡️ Инадзума",
            "sumeru": "🌿 Сумеру",
            "fontaine": "🫵 Фонтейн",
            "natlan": "🗿 Натлан",
            "other_services": "❕ Дополнительные услуги"
        }.get(region, region.capitalize())
        
        if region in LOCATION_ITEMS:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"💎 {region_name} - доступные услуги:",
                reply_markup=get_locations_keyboard(region)
            )
        else:
            bot.answer_callback_query(call.id, "Регион не найден")
    except Exception as e:
        print(f"Error in genshin_location_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка навигации. Попробуйте снова.")

@bot.callback_query_handler(func=lambda call: call.data == "genshin_locations")
def back_to_locations_handler(call):
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=PLATFORM_TEXTS["genshin_locations"],
            reply_markup=get_locations_keyboard()
        )
    except Exception as e:
        print(f"Error in back_to_locations_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка возврата. Попробуйте снова.")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_platforms")
def back_to_platforms_handler(call):
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Добро пожаловать! Выберите платформу для покупки услуги:",
            reply_markup=get_platforms_keyboard()
        )
    except Exception as e:
        print(f"Error in back_to_platforms_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка возврата. Попробуйте снова.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("item|||"))
def item_selected_handler(call):
    try:
        parts = call.data.split("|||")
        if len(parts) != 3:
            bot.answer_callback_query(call.id, "Ошибка обработки выбора")
            return
            
        platform = parts[1]
        name = parts[2]
        
        price = None
        if platform == "genshin_locations":
            for region in LOCATION_ITEMS.values():
                for n, p in region:
                    if n == name:
                        price = p
                        break
        else:
            for n, p in PLATFORM_ITEMS.get(platform, []):
                if n == name:
                    price = p
                    break
        
        if price is not None:
            kb = types.InlineKeyboardMarkup()
            confirm_callback = f"confirm|||{platform}|||{name}"
            kb.add(types.InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data=confirm_callback))
            
            if platform == "genshin_locations":
                region = get_region_by_name(name)
                if region:
                    kb.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data=f"genshin_loc|||{region}"))
            else:
                kb.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data=platform))
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Вы выбрали: {name} ({price}₽)\n\nПодтвердите заказ:",
                reply_markup=kb
            )
        else:
            bot.answer_callback_query(call.id, "Товар не найден")
    except Exception as e:
        print(f"Error in item_selected_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка при обработке выбора")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm|||"))
def confirm_order_handler(call):
    try:
        parts = call.data.split("|||")
        if len(parts) != 3:
            bot.answer_callback_query(call.id, "Ошибка подтверждения")
            return
            
        platform = parts[1]
        name = parts[2]
        
        price = None
        if platform == "genshin_locations":
            for region in LOCATION_ITEMS.values():
                for n, p in region:
                    if n == name:
                        price = p
                        break
        else:
            for n, p in PLATFORM_ITEMS.get(platform, []):
                if n == name:
                    price = p
                    break
        
        username = call.from_user.username or 'Без username'
        platform_name = dict(PLATFORMS).get(platform, platform)
        
        text = f"[НОВЫЙ ЗАКАЗ]\nПлатформа: {platform_name}\nПозиция: {name} ({price}₽)\nПользователь: @{username} ({call.from_user.id})"
        bot.send_message(MANAGER_CHAT_ID, text)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ Заказ подтвержден!\n\n{name} ({price}₽)\n\nС вами свяжется менеджер для оплаты."
        )
        
    except Exception as e:
        print(f"Error in confirm_order_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка при подтверждении заказа")

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
        kb.add(types.InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_steam"))
        kb.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="steam"))
        bot.send_message(message.chat.id, 
                        f"Логин: {login}\nСумма пополнения: {amount}₽\nКомиссия (8%): {commission}₽\nИтого к оплате: {total}₽\n\nПодтвердить заказ?",
                        reply_markup=kb)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректную сумму в рублях.")

@bot.callback_query_handler(func=lambda call: call.data == "confirm_steam")
def confirm_steam_handler(call):
    try:
        data = user_states.get(call.from_user.id, {})
        login = data.get("login")
        amount = data.get("amount")
        commission = data.get("commission")
        total = data.get("total")
        username = call.from_user.username or 'Без username'
        
        text = f"[НОВЫЙ ЗАКАЗ]\nSteam\nЛогин: {login}\nСумма: {amount}₽\nКомиссия: {commission}₽\nИтого: {total}₽\nПользователь: @{username} ({call.from_user.id})"
        bot.send_message(MANAGER_CHAT_ID, text)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ Заказ подтвержден!\n\nЛогин: {login}\nСумма: {amount}₽\nИтого: {total}₽\n\nС вами свяжется менеджер для оплаты."
        )
        user_states.pop(call.from_user.id, None)
    except Exception as e:
        print(f"Error in confirm_steam_handler: {e}")
        bot.answer_callback_query(call.id, "Ошибка при подтверждении заказа")

@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    bot.send_message(message.chat.id, "Пожалуйста, выберите платформу через меню /start.")

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
