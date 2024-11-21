#      ███████╗  █████╗   ██████╗  ███╗   ███╗
#      ██╔════╝ ██╔══██╗ ██╔═══██╗ ████╗ ████║
#      ███████╗ ███████║ ██║   ██║ ██╔████╔██║
#      ╚════██║ ██╔══██║ ██║▄▄ ██║ ██║╚██╔╝██║
#      ███████║ ██║  ██║  ██████╔╝ ██║ ╚═╝ ██║

# meta developer: @Yaukais,@Shadow_red1

# token = 7630170603:AAEMKaJHWrugihnMUGVDJTcLoKboknqP-6s
# cd /storage/emulated/0/zombie_game
# python zombie_bot.py

import telebot
import json
import os
import random
import threading
from telebot import types
from datetime import datetime, timedelta

API_TOKEN = '7630170603:AAEMKaJHWrugihnMUGVDJTcLoKboknqP-6s'
bot = telebot.TeleBot(API_TOKEN)

PROFILES_FILE = 'user_profiles.json'
ADMIN_ID = '6365361106'  # ID создателя бота

# Проверка существования файла и загрузка профилей
if os.path.exists(PROFILES_FILE):
    try:
        with open(PROFILES_FILE, 'r') as file:
            user_profiles = json.load(file)
    except json.JSONDecodeError as e:
        print(f'Ошибка при загрузке JSON: {e}')
        user_profiles = {}
else:
    user_profiles = {}

GENERATOR_LEVELS = {
    "водяной": {"experience": 0, "energy": 1, "nails": 50},
    "угольный": {"experience": 500, "energy": 4, "nails": 200},
    "древесный": {"experience": 2000, "energy": 8, "nails": 400},
    "нефтяной": {"experience": 10000, "energy": 26, "nails": 1200},
    "ветреной": {"experience": 25000, "energy": 58, "nails": 7500},
    "солнечный": {"experience": 60000, "energy": 142, "nails": 40000},
    "ядерной": {"experience": 100000, "energy": 800, "nails": 120000}
}

def initialize_profile(user_id, first_name):
    return {
        "profile_created": True,
        "status": "Игрок",
        "level": 1,
        "experience": 0,
        "w_coin": 0,
        "balance": 0,
        "base_level": 1,
        "registration_date": datetime.now().strftime("%d.%m.%Y"),
        "nails": {
            "rusty": 0,
            "broken": 0,
            "normal": 0,
            "golden": 0,
            "platinum": 0
        },
        "last_bonus_claim": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "weapons": 0,
        "medkits": 0,
        "exploration_history": [],
        "promo_codes_used": [],
        "avatar": None,
        "water": 20,
        "energy": 0,
        "generator_experience": 0,
        "generator_type": "водяной",
        "exploration_success": False,
        "first_name": first_name
    }

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = str(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Создать базу", callback_data='create_profile')
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в BFG|Zombie attack! Для создания игрового профиля нажмите кнопку ниже.\n"
        "Для просмотра профиля напишите - <code>База</code>.",
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'create_profile')
def handle_create_profile_callback(call):
    user_id = str(call.from_user.id)
    first_name = call.from_user.first_name
    if user_id not in user_profiles:
        user_profiles[user_id] = initialize_profile(user_id, first_name)
        save_profiles()
        bot.send_message(call.message.chat.id, "Ваш игровой профиль создан! \nНапишите - <code>База</code> , для просмотра профиля.", parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "Профиль уже существует. Напишите - <code>База</code> , для просмотра профиля.", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text.lower() in ["база", "б"])
def view_profile(message):
    user_id = str(message.from_user.id)
    if user_id in user_profiles and user_profiles[user_id]["profile_created"]:
        profile_info = user_profiles[user_id]
        water = profile_info.get('water', 0)
        energy = profile_info.get('energy', 0)
        nails = profile_info.get('nails', {}).get('normal', 0)

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("Мой генератор", callback_data='my_generator'),
            types.InlineKeyboardButton("Инфо генератор", callback_data='generator_info'),
            types.InlineKeyboardButton("Исследовать запретную зону", callback_data='explore_zone'),
            types.InlineKeyboardButton("Помощь", callback_data='help'),
            types.InlineKeyboardButton("Инвентарь", callback_data='inventory'),
            types.InlineKeyboardButton("Склад", callback_data='storage'),
            types.InlineKeyboardButton("Промокод", callback_data='promo_code'),
            types.InlineKeyboardButton("Обмен ВИП", callback_data='exchange_w_coin'),
            types.InlineKeyboardButton("История исследований", callback_data='exploration_history'),
            types.InlineKeyboardButton("Загрузить аватарку по URL", callback_data='upload_avatar_url'),
            types.InlineKeyboardButton("Удалить аватарку", callback_data='remove_avatar'),
            types.InlineKeyboardButton("Улучшить базу", callback_data='upgrade_base'),
            types.InlineKeyboardButton("Рейд", callback_data='raid_instructions')
        )

        if profile_info.get("avatar"):
            bot.send_photo(message.chat.id, profile_info["avatar"], caption="🌐 Ваш аватар:")
        else:
            bot.send_message(message.chat.id, "🌐 Ваш аватар: Нет аватарки.")

        profile_message = (
            f"👤 Ваш профиль:\n"
            f"🆔 : {user_id}\n"
            f"🏢 Статус: {profile_info['status']}\n"
            f"🪙 ŵ-coin: {profile_info.get('w_coin', 0)}\n"
            f"🔩 Баланс: {profile_info.get('balance', 0)} гв.\n"
            f"📊 Уровень базы: {profile_info.get('base_level', 1)}\n"
            f"⭐️ Опыт: {profile_info['experience']}\n"
            f"📅 Дата регистрации: {profile_info['registration_date']}\n"
            f"💧 Вода: {water}/20 л.\n"
            f"⚡️ Энергия: {energy} шт.\n"
            f"🔩 Гвоздей: {nails} шт.\n"
        )

        bot.send_message(message.chat.id, profile_message, parse_mode='HTML', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Сначала создайте профиль, написав - <code>/start</code>.", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == 'my_generator')
def my_generator(call):
    user_id = str(call.from_user.id)
    profile_info = user_profiles[user_id]

    generator_message = (
        f"{profile_info['first_name']}, информация о твоём генераторе:\n"
        f"⭐️ Опыт: {profile_info['generator_experience']}\n"
        f"💧 Вода: {profile_info['water']}/20 л.\n"
        f"🏭 Тебе доступно: {profile_info['generator_type']}\n"
        f"\n📦 Твой склад:\n"
        f"⚡️ Энергия - {profile_info['energy']} шт.\n"
        f"🔩 Гвоздей - {profile_info['nails']['normal']} шт."
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Запустить генератор", callback_data='start_generator'))
    bot.send_message(call.message.chat.id, generator_message, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'start_generator')
def start_generator(call):
    user_id = str(call.from_user.id)
    profile_info = user_profiles[user_id]

    if profile_info['water'] > 0:
        generator = GENERATOR_LEVELS[profile_info['generator_type']]
        energy_generated = generator['energy']
        nails_generated = generator['nails']
        experience_gained = random.choice([1, 2, 4, 6, 8, 10])

        profile_info['water'] -= 1
        profile_info['energy'] += energy_generated
        profile_info['nails']['normal'] += nails_generated
        profile_info['generator_experience'] += experience_gained

        check_upgrade(user_id)

        save_profiles()

        bot.send_message(call.message.chat.id, f"{profile_info['first_name']}, ты успешно завершил работу генератора!\n"
                                                f"Получено: {energy_generated} ⚡️ энергии, 🔩 {nails_generated} гвоздей, {experience_gained} ⭐️ опыта\n"
                                                f"Потрачено: 1 вода\n"
                                                f"Осталось воды: {profile_info['water']} 💧")
    else:
        bot.send_message(call.message.chat.id, f"{profile_info['first_name']}, у тебя не хватает воды 💧!")

def check_upgrade(user_id):
    profile_info = user_profiles[user_id]
    for generator, requirements in GENERATOR_LEVELS.items():
        if generator != profile_info['generator_type'] and profile_info['generator_experience'] >= requirements['experience']:
            profile_info['generator_type'] = generator
            bot.send_message(user_id, f"{profile_info['generator_type'].capitalize()} генератор теперь доступен!")

@bot.callback_query_handler(func=lambda call: call.data == 'generator_info')
def generator_info(call):
    generator_message = f"{call.from_user.first_name}, вот виды генераторов:\n"
    for generator, requirements in GENERATOR_LEVELS.items():
        generator_message += f"{requirements['energy']} ⚡️ {generator.capitalize()} - {requirements['experience']} опыта\n"
    bot.send_message(call.message.chat.id, generator_message)

@bot.callback_query_handler(func=lambda call: call.data == 'explore_zone')
def explore_zone(call):
    user_id = str(call.from_user.id)
    profile_info = user_profiles[user_id]

    if profile_info['energy'] >= 1:
        success = random.choice([True, False])
        if success:
            found_nails = random.randint(5, 20)
            profile_info['nails']['normal'] += found_nails
            profile_info['energy'] -= 1
            profile_info['exploration_success'] = True
            profile_info['exploration_history'].append({
                "nails_found": found_nails,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            bot.send_message(call.message.chat.id, f"{profile_info['first_name']}, вы успешно исследовали запретную зону!\n"
                                                    f"Вы нашли 🔩 {found_nails} гвоздей!")
        else:
            profile_info['energy'] -= 1
            profile_info['exploration_success'] = False
            bot.send_message(call.message.chat.id, f"{profile_info['first_name']}, исследование не увенчалось успехом.\n"
                                                    f"Энергия потрачена.")
    else:
        bot.send_message(call.message.chat.id, f"{profile_info['first_name']}, у тебя недостаточно энергии для исследования!")

@bot.callback_query_handler(func=lambda call: call.data == 'exploration_history')
def show_exploration_history(call):
    user_id = str(call.from_user.id)
    profile_info = user_profiles[user_id]
    
    if profile_info["exploration_history"]:
        history_message = "История исследований:\n"
        for record in profile_info["exploration_history"]:
            history_message += f"- Найдено гвоздей: {record['nails_found']} в {record['timestamp']}\n"
        bot.send_message(call.message.chat.id, history_message)
    else:
        bot.send_message(call.message.chat.id, "История исследований пуста.")

@bot.callback_query_handler(func=lambda call: call.data == 'help')
def send_help(call):
    help_text = ("Команды:\n"
                 "/start - Начать игру\n"
                 "База | Б - Показать свой профиль\n"
                 "Исследовать запретную зону - Начать исследование\n"
                 "Мой генератор - Посмотреть состояние генератора\n"
                 "Инфо генератор - Узнать о типах генераторов\n"
                 "Купить оружие - Купить оружие\n"
                 "Купить медикаменты - Купить медикаменты\n"
                 "История исследований - Показать историю всех исследований\n"
                 "Бонус - Получить бонус\n"
                 "Промокод - Ввести промокод")
    bot.send_message(call.message.chat.id, help_text)

@bot.callback_query_handler(func=lambda call: call.data == 'inventory')
def send_inventory(call):
    user_id = str(call.from_user.id)
    if user_id in user_profiles:
        nails_info = user_profiles[user_id]["nails"]
        inventory_text = "Ваш инвентарь:\n"
        for nail_type, amount in nails_info.items():
            inventory_text += f"{nail_type.capitalize()}: {amount}\n"
        bot.send_message(call.message.chat.id, inventory_text)
    else:
        bot.send_message(call.message.chat.id, "Сначала создайте профиль, написав - <code>/start</code>.", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == 'storage')
def send_storage(call):
    user_id = str(call.from_user.id)
    if user_id in user_profiles:
        profile_info = user_profiles[user_id]
        storage_text = (f"Ваш склад:\n"
                        f"Оружие: {profile_info['weapons']}\n"
                        f"Медикаменты: {profile_info['medkits']}")
        bot.send_message(call.message.chat.id, storage_text)
    else:
        bot.send_message(call.message.chat.id, "Сначала создайте профиль, написав - <code>/start</code>.", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text.lower() == "бонус")
def claim_bonus(message):
    user_id = str(message.from_user.id)
    if user_id in user_profiles:
        profile_info = user_profiles[user_id]
        last_claim_time = datetime.strptime(profile_info["last_bonus_claim"], "%Y-%m-%dT%H:%M:%S")
        if datetime.now() - last_claim_time >= timedelta(hours=24):
            profile_info["nails"]["normal"] += 1000  # Добавляем 1000 гвоздей
            profile_info["last_bonus_claim"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            save_profiles()
            bot.send_message(message.chat.id, "Вы получили бонус: 1000 гвоздей!")
        else:
            time_remaining = timedelta(hours=24) - (datetime.now() - last_claim_time)
            bot.send_message(message.chat.id, f"Бонус доступен через {time_remaining}.")
    else:
        bot.send_message(message.chat.id, "Сначала создайте профиль, написав - <code>/start</code>.", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == 'promo_code')
def promo_code(call):
    bot.send_message(call.message.chat.id, "Введите промокод в формате 'промокод: <ваш_код>':")

@bot.message_handler(func=lambda message: message.text.lower().startswith("промокод: "))
def handle_promo_code_input(message):
    user_id = str(message.from_user.id)
    promo_code = message.text.split(": ")[1].strip()
    success, amount = activate_promo_code(user_id, promo_code)

    if success:
        user_profiles[user_id]["w_coin"] += amount
        save_profiles()
        bot.send_message(message.chat.id, f"Промокод активирован! Вы получили {amount} ŵ-coin.")
    elif amount == 0:
        bot.send_message(message.chat.id, "Этот промокод уже был использован.")
    else:
        bot.send_message(message.chat.id, "Неверный промокод.")

@bot.callback_query_handler(func=lambda call: call.data == 'upload_avatar_url')
def request_avatar_url(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, отправьте URL для загрузки аватара.")

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def upload_avatar(message):
    user_id = str(message.from_user.id)
    user_profiles[user_id]["avatar"] = message.text
    save_profiles()
    bot.send_message(message.chat.id, "Ваш аватар успешно обновлён.")

@bot.callback_query_handler(func=lambda call: call.data == 'remove_avatar')
def remove_avatar(call):
    user_id = str(call.from_user.id)
    user_profiles[user_id]["avatar"] = None
    save_profiles()
    bot.send_message(call.message.chat.id, "Ваша аватарка была успешно удалена.")

@bot.callback_query_handler(func=lambda call: call.data == 'exchange_w_coin')
def exchange_w_coin(call):
    bot.send_message(call.message.chat.id, "Введите команду для обмена, например:\n'<code>обменять 1 R</code>'\n'<code>обменять 1 B</code>'\n'<code>обменять 1 N</code>'\n'<code>обменять 1 G</code>'\n'<code>обменять 1 P</code>'.",parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text.lower().startswith("обменять"))
def exchange_vip(message):
    user_id = str(message.from_user.id)
    try:
        parts = message.text.split()
        quantity = int(parts[1])
        nail_type = parts[2].upper()
        
        exchange_rates = {
            "R": ("rusty", 500000),
            "B": ("broken", 50000),
            "N": ("normal", 5000),
            "G": ("golden", 500),
            "P": ("platinum", 50)
        }

        if nail_type in exchange_rates:
            nail_name, nails_per_unit = exchange_rates[nail_type]
            total_nails = nails_per_unit * quantity
            profile_info = user_profiles[user_id]
            if profile_info['w_coin'] >= quantity:  # Проверяем достаточно ли ВИП валюты
                profile_info['w_coin'] -= quantity  # Уменьшаем ВИП валюту
                profile_info['nails'][nail_name] += total_nails  # Добавляем гвозди
                save_profiles()
                bot.send_message(message.chat.id, f"Вы обменяли {quantity} ŵ-coin на {total_nails} {nail_name} гвоздей.")
            else:
                bot.send_message(message.chat.id, "Недостаточно ВИП валюты для обмена!")
        else:
            bot.send_message(message.chat.id, "Неверный тип гвоздей для обмена!")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Введите команду в формате: 'обменять <количество> <тип>'")

@bot.callback_query_handler(func=lambda call: call.data == 'upgrade_base')
def upgrade_base(call):
    user_id = str(call.from_user.id)
    profile_info = user_profiles[user_id]

    required_energy = 30
    required_nails = 15000  # Примерная стоимость улучшения

    if profile_info['energy'] >= required_energy and profile_info['nails']['normal'] >= required_nails:
        profile_info['energy'] -= required_energy
        profile_info['nails']['normal'] -= required_nails
        profile_info['base_level'] += 1  # Увеличиваем уровень базы
        save_profiles()
        bot.send_message(call.message.chat.id, f"База успешно улучшена до уровня {profile_info['base_level']}!")
    else:
        bot.send_message(call.message.chat.id, f"Недостаточно ресурсов для улучшения базы.\nВам нужно {required_energy} энергии и {required_nails} нормальных гвоздей.")

@bot.callback_query_handler(func=lambda call: call.data == 'raid_instructions')
def raid_instructions(call):
    bot.send_message(call.message.chat.id, "Чтобы запустить рейд, напишите 'Рейд <ID>', где <ID> - это ID пользователя, которого вы хотите зарейдить.")

@bot.message_handler(func=lambda message: message.text.lower().startswith("рейд"))
def raid_user(message):
    user_id = str(message.from_user.id)
    target_id = message.text.split()[1]  # Получаем ID цели

    if target_id not in user_profiles:
        bot.send_message(message.chat.id, "Пользователь не найден.")
        return

    profile_info = user_profiles[user_id]
    target_info = user_profiles[target_id]

    # Проверяем наличие необходимого ресурса
    if profile_info['weapons'] < 5 or profile_info['medkits'] < 7:
        bot.send_message(message.chat.id, f"Недостаточно ресурсов для рейда!\nВам нужно 5 оружия и 7 медикаментов.")
        return

    # Уменьшаем ресурсы
    profile_info['weapons'] -= 5
    profile_info['medkits'] -= 7

    save_profiles()

    bot.send_message(message.chat.id, "Рейд запущен, через 30 секунд он закончится.")
    
    # Запускаем таймер на 30 секунд
    threading.Timer(30, complete_raid, args=(user_id, target_id)).start()

def complete_raid(user_id, target_id):
    profile_info = user_profiles[user_id]
    target_info = user_profiles[target_id]
    
    success = random.choice([True, False])  # Случайный успех/неудача рейда
    if success:
        earned_rating = random.randint(60, 120)
        target_loss = earned_rating // 2
        profile_info['rating'] += earned_rating  # Увеличиваем рейтинг
        target_info['rating'] -= target_loss  # Уменьшаем рейтинг цели

        bot.send_message(user_id, f"{profile_info['first_name']} вы успешно зарейдили {target_info['first_name']} на {earned_rating} рейтинга!")
        bot.send_message(target_id, f"{target_info['first_name']} вы были зарейдены и потеряли {target_loss} рейтинга.")
    else:
        penalty = random.choice([30, 120])
        profile_info['rating'] -= penalty  # Уменьшаем рейтинг
        bot.send_message(user_id, f"Рейд не удался! Вы потеряли {penalty} рейтинга.")

def save_profiles():
    with open(PROFILES_FILE, 'w') as file:
        json.dump(user_profiles, file, indent=4)

@bot.message_handler(func=lambda message: message.from_user.id in user_profiles)
def update_user_name(message):
    user_id = str(message.from_user.id)
    user_profiles[user_id]["first_name"] = message.from_user.first_name
    save_profiles()

@bot.callback_query_handler(func=lambda call: True)  # Обработчик для всех других кнопок
def handle_invalid_button(call):
    user_id = str(call.from_user.id)
    if user_id in user_profiles:
        bot.send_message(call.message.chat.id, "Это не ваша база, вы не можете нажимать на эти кнопки!")
    else:
        bot.send_message(call.message.chat.id, "Сначала создайте профиль, написав - <code>/start</code>.", parse_mode='HTML')

if __name__ == '__main__':
    bot.polling(none_stop=True)