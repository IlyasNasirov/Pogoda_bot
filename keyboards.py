from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import requests as rq
from template import template

choice_lang = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Русский", callback_data="ru")],
    [InlineKeyboardButton(text="English", callback_data="en")],
    [InlineKeyboardButton(text="O'zbek", callback_data="uz")],
])


async def languages(lang):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Русский'), KeyboardButton(text='English'), KeyboardButton(text="O'zbekcha")],
        [KeyboardButton(text=template[lang]['main_btn'])]],
        resize_keyboard=True)


async def send_location(lang):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=template[lang]['share_loc_btn'], request_location=True)]
    ], resize_keyboard=True)


async def main_menu(lang):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=f"{template[lang]['weather_now_btn']}"),
         KeyboardButton(text=f"{template[lang]['weather_tomorrow_btn']}")],
        [KeyboardButton(text=f"{template[lang]['weather_7_btn']}"),
         KeyboardButton(text=f"{template[lang]['weather_14_btn']}")],
        [KeyboardButton(text=f"{template[lang]['notify_btn']}"),
         KeyboardButton(text=f"{template[lang]['location_btn']}")],
        [KeyboardButton(text=f"{template[lang]['change_lang_btn']}"),
         KeyboardButton(text=f"{template[lang]['feedback_btn']}")],
    ], resize_keyboard=True)


async def back_to_main(lang):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=f"{template[lang]['main_btn']}")]], resize_keyboard=True)


async def hours_menu(lang):
    keyboard = InlineKeyboardBuilder()
    for i in range(24):
        keyboard.add(InlineKeyboardButton(text=f"{i:02}:00", callback_data=f"hour_{i}"))
    keyboard.add(InlineKeyboardButton(text=f"{template[lang]['back_btn']}", callback_data="back_to_notify"))
    return keyboard.adjust(4).as_markup()


async def my_notif_menu(user_id, lang):
    keyboard = InlineKeyboardBuilder()
    notifications = await rq.get_notifies_by_user_id(user_id)
    for notify in notifications:
        keyboard.add(InlineKeyboardButton(text=f"{notify.hour:02}:00", callback_data='noop'))
        keyboard.add(InlineKeyboardButton(text='❌', callback_data=f"del_hour_{notify.hour}"))
    keyboard.add(InlineKeyboardButton(text=f"{template[lang]['main_btn']}", callback_data="back_to_main"))
    keyboard.add(InlineKeyboardButton(text=f"{template[lang]['add_btn']}", callback_data="add_hour"))
    return keyboard.adjust(2).as_markup()
