from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
import json


with open("data.json", "r", encoding="utf-8") as file:
    translations = json.load(file)

def get_text(lang, category, key):
    return translations.get(lang, {}).get(category, {}).get(key, f"[{key}]")

def start_key():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=f"🇺🇸 eng"), KeyboardButton(text=f"🇺🇿 uz"),KeyboardButton(text=f"🇷🇺 ru"))
    keyboard.adjust(3)
    return keyboard.as_markup(resize_keyboard=True)


def customer_or_master(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'customer')), KeyboardButton(text=get_text(lang, 'buttons', 'master')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)

def phone_key(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'contact'),request_contact=True))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def skip_message(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
                 KeyboardButton(text=get_text(lang, 'buttons', 'skip')))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def location(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'location'), request_location=True))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)



def conf(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'confirm')), KeyboardButton(text=get_text(lang, 'buttons', 'rejected')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


def waited_confirmation(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
                 KeyboardButton(text=get_text(lang, 'buttons', 'conf_admin')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'cancel_master_info')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'contact_with_admin')))
    keyboard.adjust(2,1)
    return keyboard.as_markup(resize_keyboard=True)






def conf_new_user(lang,user_id):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.add(
        InlineKeyboardButton(text=get_text(lang, "buttons", "confirm_new_master"), callback_data=f"approve:{user_id}"),
        InlineKeyboardButton(text=get_text(lang, "buttons", "rejected_new_master"), callback_data=f"reject:{user_id}"),
    )
    inline_keyboard.adjust(2)
    return inline_keyboard.as_markup()





def registered_master(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
                 KeyboardButton(text=get_text(lang, 'buttons', 'mijozlar')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'vaqt')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'rating')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_info_master')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)





def select_change_info(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_name_master')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_phone_master')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_manzil_master')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_moljal_master')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_lokatsiya_master')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_working_tim_master')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_working_min_master')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)





def generate_date_keyboard():
    kb = InlineKeyboardBuilder()
    today = datetime.today()
    for i in range(7):
        date = today + timedelta(days=i)
        formatted_date = date.strftime("%d.%m.%Y")  # Masalan: 21.07.2025
        kb.add(InlineKeyboardButton(text=formatted_date, callback_data=f"date:{formatted_date}"))
    kb.adjust(3)  # Har qatorda 3 ta tugma
    return kb.as_markup()


def back(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def menu(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'services')), KeyboardButton(text=get_text(lang, 'buttons', 'service_type')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_info')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)



def change_info(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'change_phone')), KeyboardButton(text=get_text(lang, 'buttons', 'change_name')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'change_lang')),KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2,1)
    return keyboard.as_markup(resize_keyboard=True)



def change_lang(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'eng')), KeyboardButton(text=get_text(lang, 'buttons', 'uz')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'ru')),KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(3,1)
    return keyboard.as_markup(resize_keyboard=True)





