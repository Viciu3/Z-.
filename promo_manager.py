#      ███████╗  █████╗   ██████╗  ███╗   ███╗
#      ██╔════╝ ██╔══██╗ ██╔═══██╗ ████╗ ████║
#      ███████╗ ███████║ ██║   ██║ ██╔████╔██║
#      ╚════██║ ██╔══██║ ██║▄▄ ██║ ██║╚██╔╝██║
#      ███████║ ██║  ██║  ██████╔╝ ██║ ╚═╝ ██║

# meta developer: @Yaukais,@Shadow_red1

import json
import os

PROMO_CODES_FILE = 'promo_codes.json'

# Проверка существования файла и загрузка промокодов
if os.path.exists(PROMO_CODES_FILE):
    try:
        with open(PROMO_CODES_FILE, 'r') as file:
            promo_codes = json.load(file)
    except json.JSONDecodeError as e:
        print(f'Ошибка при загрузке JSON: {e}')
        promo_codes = {}
else:
    promo_codes = {}

def get_promo_codes():
    return promo_codes

def save_promo_codes():
    with open(PROMO_CODES_FILE, 'w') as file:
        json.dump(promo_codes, file, indent=4)  # Добавлен отступ для форматирования

def activate_promo_code(user_id, promo_code):
    if promo_code not in promo_codes:
        promo_codes[promo_code] = {'used': False}

    if promo_code == "test":
        if not promo_codes[promo_code]['used'] and user_id == '6365361106':
            promo_codes[promo_code]['used'] = True
            return True, 999999  # Возвращаем True и количество ŵ-coin, которое нужно добавить
        else:
            return False, 0  # Промокод уже использован или не для этого пользователя

    elif promo_code == "Owl":
        if not promo_codes[promo_code]['used'] and user_id == '6399039163':
            promo_codes[promo_code]['used'] = True
            return True, 99  # Возвращаем True и количество ŵ-coin, которое нужно добавить
        else:
            return False, 0  # Промокод уже использован или не для этого пользователя

    else:
        return False, 0  # Неверный промокод   