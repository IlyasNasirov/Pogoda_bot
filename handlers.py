from aiogram import F, Router
from aiogram.filters import CommandStart, or_f, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import api_clients as client
import requests as rq
import keyboards as kb
from States import UserStates
from sessions import set_session, get_session
from template import template

from datetime import datetime, timedelta

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.from_user.username
    lang = message.from_user.language_code
    user = await rq.set_user(user_id, name)
    if not user.language:
        await message.answer(f"{template[lang]['start']}", reply_markup=kb.choice_lang)
        return
    if not user.location:
        user = await get_session(user_id)
        await message.answer(f"{template[user['language']]['share_location']}",
                             reply_markup=await kb.send_location(lang))
        return
    else:
        await main_menu(message, f"{template[lang]['main']}", state)


@router.callback_query(F.data.in_(['ru', 'en', 'uz']))
async def set_language(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data
    await state.set_state(UserStates.location)
    await set_session(user_id, language=lang)
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(f"{template[lang]['share_location']}", reply_markup=await kb.send_location(lang))


@router.message(or_f(F.location, StateFilter(UserStates.location)))
async def send_location(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        coordinates = f"{latitude},{longitude}"
        city = await client.get_city(coordinates)
        choose_city = template[lang]['choose_city']
        if not str(city).isdigit():
            await set_session(user_id, location=city)
            await  main_menu(message, choose_city.format(city), state)
        else:
            await message.answer(f"{template[lang]['no_such_city']}")
            return
    else:
        city = await client.get_city(message.text)
        if not city.startswith('Error'):
            await set_session(user_id, location=city)
            choose_city = template[lang]['choose_city']
            await  main_menu(message, choose_city.format(city), state)
        else:
            await message.answer(f"{template[lang]['no_such_city']}")
            return


async def main_menu(message: Message, text, state: FSMContext):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await state.clear()
    await message.answer(text, reply_markup=await kb.main_menu(lang))


@router.message(F.text.in_(["☀️ Weather Now", "☀️ Погода сейчас", "☀️ Hozirgi ob-havo"]))
async def weather_now(message: Message):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    current = await client.current(user['location'])
    today = await client.today(user['location'])

    region = user['location']
    temp = current['current']['temp_c']
    text = current['current']['condition']['text'].strip().lower()
    wind_kph = current['current']['wind_kph']
    humidity = current['current']['humidity']
    feels_like = current['current']['feelslike_c']
    pressure_mb = current['current']['pressure_mb']
    max_t = today['day']['maxtemp_c']
    min_t = today['day']['mintemp_c']
    rain = today['day']['daily_chance_of_rain']
    snow = today['day']['daily_chance_of_snow']
    rain_line = f"*🌧 {template[lang]['chance_of_rain']}:* `{rain}%`\n" if rain > 0 else ""
    snow_line = f"*❄️ {template[lang]['chance_of_snow']}:* `{snow}%`" if snow > 0 else ""

    now = datetime.now()
    day = template[lang][now.strftime("%A")]
    month = template[lang][now.strftime("%B")]
    date = f"{day}, {now.day} {month}"

    current_text = template[lang]['current']
    feels_text = template[lang]['feels']
    wind_text = template[lang]['wind']
    humidity_text = template[lang]['humidity']
    pressure_text = template[lang]['pressure']
    kph_text = template[lang]['kph']
    mmhg_text = template[lang]['mmhg']

    weather_message = (
        f"*📍 {region}*\n"
        f"*🗓️ {date}*\n\n"
        f"*🌡 {current_text}:* `{temp}°C` _({feels_text} {feels_like}°C)_\n"
        f"*{template[user['language']][text]}*\n\n"
        f"🔆 `{max_t}°C`  🌙 `{min_t}°C`\n"
        f"*💨 {wind_text}:* `{wind_kph} {kph_text}`*💧 {humidity_text}:* `{humidity}%`\n*🌬 {pressure_text}:*"
        f" `{pressure_mb} {mmhg_text}`\n\n"
        f"{rain_line}{snow_line}"
    )
    await message.answer(weather_message)


@router.message(F.text.in_(["🌤 Tomorrow's Weather", "🌤️ Погода на завтра", "🌤️ Ertangi ob-havo"]))
async def weather_tomorrow(message: Message):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    tomorrow = await client.tomorrow(user['location'])

    max_t = tomorrow['day']['maxtemp_c']
    min_t = tomorrow['day']['mintemp_c']
    text = tomorrow['day']['condition']['text'].strip().lower()
    wind_kph = tomorrow['hour'][13]['wind_kph']
    humidity = tomorrow['day']['avghumidity']
    pressure_mb = tomorrow['hour'][13]['pressure_mb']
    rain = tomorrow['day']['daily_chance_of_rain']
    snow = tomorrow['day']['daily_chance_of_snow']
    rain_line = f"*🌧 {template[lang]['chance_of_rain']}:* `{rain}%`\n" if rain > 0 else ""
    snow_line = f"*❄️ {template[lang]['chance_of_snow']}:* `{snow}%`" if snow > 0 else ""

    date_tomorrow = datetime.now() + timedelta(days=1)
    day = template[lang][date_tomorrow.strftime("%A")]
    month = template[lang][date_tomorrow.strftime("%B")]
    date = f"{day}, {date_tomorrow.day} {month}"

    wind_text = template[lang]['wind']
    humidity_text = template[lang]['humidity']
    pressure_text = template[lang]['pressure']
    kph_text = template[lang]['kph']
    mmhg_text = template[lang]['mmhg']
    weather_message = (
        f"*📍 {user['location']}*\n"
        f"*🗓️ {date}*\n\n"
        f"🔆 `{max_t}°C`  🌙 `{min_t}°C`\n"
        f"*{template[user['language']][text]}*\n\n"
        f"*💨 {wind_text}:* `{wind_kph} {kph_text}`*💧 {humidity_text}:* `{humidity}%`\n*🌬 {pressure_text}:*"
        f" `{pressure_mb} {mmhg_text}`\n\n"
        f"{rain_line}{snow_line}"
    )
    await message.answer(weather_message)


@router.message(F.text.in_(["🗓️ 7-Day Weather", "🗓️ Прогноз на 7 дней", "🗓️ 7 kunlik ob-havo"]))
async def weather_week(message: Message):
    user = await get_session(message.from_user.id)
    lang = user['language']
    data = await client.forecast(user['location'], 7)
    weather_message = f"*📍 {user['location']}*\n\n"
    for i in range(7):
        now = datetime.strptime(data['forecast']['forecastday'][i]['date'], "%Y-%m-%d")
        day = template[lang][now.strftime("%A")]
        month = template[lang][now.strftime("%B")]
        date = f"{day}, {now.day} {month}"
        max_t = data['forecast']['forecastday'][i]['day']['maxtemp_c']
        min_t = data['forecast']['forecastday'][i]['day']['mintemp_c']
        text = data['forecast']['forecastday'][i]['day']['condition']['text'].strip().lower()
        rain = data['forecast']['forecastday'][i]['day']['daily_chance_of_rain']
        snow = data['forecast']['forecastday'][i]['day']['daily_chance_of_snow']
        rain_line = f" 🌧 `{rain}%`" if rain > 0 else ""
        snow_line = f" ❄️ `{snow}%`" if snow > 0 else ""
        weather_message += (
            f"*🗓️ {date}*\n"
            f"🔆 `{max_t}°C`  🌙 `{min_t}°C`\n"
            f"*{template[lang][text]}*{rain_line}{snow_line}\n\n"
        )
    await message.answer(weather_message)


@router.message(F.text.in_(["🗓 14-Day Weather", "🗓️ Прогноз на 14 дней", "🗓️ 14 kunlik ob-havo"]))
async def weather_two_week(message: Message):
    user = await get_session(message.from_user.id)
    lang = user['language']
    data = await client.forecast(user['location'], 14)
    weather_message = f"*📍 {user['location']}*\n\n"
    for i in range(14):
        now = datetime.strptime(data['forecast']['forecastday'][i]['date'], "%Y-%m-%d")
        day = template[lang][now.strftime("%A")]
        month = template[lang][now.strftime("%B")]
        date = f"{day}, {now.day} {month}"
        max_t = data['forecast']['forecastday'][i]['day']['maxtemp_c']
        min_t = data['forecast']['forecastday'][i]['day']['mintemp_c']
        text = data['forecast']['forecastday'][i]['day']['condition']['text'].strip().lower()
        rain = data['forecast']['forecastday'][i]['day']['daily_chance_of_rain']
        snow = data['forecast']['forecastday'][i]['day']['daily_chance_of_snow']
        rain_line = f" 🌧 `{rain}%`" if rain > 0 else ""
        snow_line = f" ❄️ `{snow}%`" if snow > 0 else ""
        weather_message += (
            f"*🗓️ {date}*\n"
            f"🔆 `{max_t}°C`  🌙 `{min_t}°C`\n"
            f"*{template[lang][text]}*{rain_line}{snow_line}\n\n"
        )
    await message.answer(weather_message)


@router.message(F.text.in_(["🔔 My notifications", "🔔 Мои уведомления", "🔔 Mening bildirishnomalarim"]))
async def my_notifications_menu(message: Message):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await message.answer(f"{template[lang]['notify_menu']}", reply_markup=await kb.my_notif_menu(user_id, lang))


@router.message(F.text.in_(["🌐 Change Language", "🌐 Изменить язык", "🌐 Tilni o‘zgartirish"]))
async def language_menu(message: Message):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await message.answer(f"{template[lang]['choose_lang']}", reply_markup=await kb.languages(lang))


@router.message(F.text.in_(["Русский", "English", "O'zbekcha"]))
async def set_language(message: Message):
    change_lang = {
        "Русский": 'ru',
        "English": 'en',
        "O'zbekcha": 'uz',
    }
    user_id = message.from_user.id
    lang = change_lang[message.text]
    await set_session(user_id, language=lang)
    await message.answer(f"{template[lang]['changed_lang']}", reply_markup=await kb.main_menu(lang))


@router.message(F.text.in_(["📍 Change Location", "📍 Изменить местоположение", "📍 Joylashuvni o‘zgartirish"]))
async def change_location_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await state.set_state(UserStates.location)
    await message.answer(f"{template[lang]['share_location']}", reply_markup=await kb.send_location(lang))


@router.message(F.text.in_(["📝 Send Feedback", "📝 Оставить отзыв", "📝 Fikr qoldirish"]))
async def feedback_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await state.set_state(UserStates.feedback)
    await message.answer(f"{template[lang]['leave_feedback']}", reply_markup=await kb.back_to_main(lang))


@router.message(UserStates.feedback)
async def save_feedback(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    if message.text in (["🏠 Main menu", "🏠 Главное меню", "🏠 Asosiy menyu"]):
        await main_menu(message, f"{template[lang]['main']}", state)
        return
    from main import bot
    text = f"{message.from_user.username or message.from_user.full_name}: {message.text}"
    await bot.send_message(1332835850, text)
    await message.answer(f"{template[lang]['feedback_success']}", reply_markup=await kb.main_menu(lang))


@router.message(F.text.in_(["🏠 Main menu", "🏠 Главное меню", "🏠 Asosiy menyu"]))
async def back_to_main(message: Message):
    user_id = message.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await message.answer(f"{template[lang]['main']}", reply_markup=await kb.main_menu(lang))


@router.message()
async def handle_everything(message: Message):
    user = await get_session(message.from_user.id)
    lang = user['language']
    city = await client.get_city(message.text)
    if not city.startswith('Error'):
        current = await client.current(city)
        today = await client.today(city)

        region = current['location']['name']
        temp = current['current']['temp_c']
        text = current['current']['condition']['text'].strip().lower()
        wind_kph = current['current']['wind_kph']
        humidity = current['current']['humidity']
        feels_like = current['current']['feelslike_c']
        pressure_mb = current['current']['pressure_mb']
        max_t = today['day']['maxtemp_c']
        min_t = today['day']['mintemp_c']
        rain = today['day']['daily_chance_of_rain']
        snow = today['day']['daily_chance_of_snow']
        rain_line = f"*🌧 {template[lang]['chance_of_rain']}:* `{rain}%`\n" if rain > 0 else ""
        snow_line = f"*❄️ {template[lang]['chance_of_snow']}:* `{snow}%`" if snow > 0 else ""

        now = datetime.now()
        day = template[lang][now.strftime("%A")]
        month = template[lang][now.strftime("%B")]
        date = f"{day}, {now.day} {month}"

        current_text = template[lang]['current']
        feels_text = template[lang]['feels']
        wind_text = template[lang]['wind']
        humidity_text = template[lang]['humidity']
        pressure_text = template[lang]['pressure']
        kph_text = template[lang]['kph']
        mmhg_text = template[lang]['mmhg']

        weather_message = (
            f"*📍 {region}*\n"
            f"*🗓️ {date}*\n\n"
            f"*🌡 {current_text}:* `{temp}°C` _({feels_text} {feels_like}°C)_\n"
            f"*{template[lang][text]}*\n\n"
            f"🔆 `{max_t}°C`  🌙 `{min_t}°C`\n"
            f"*💨 {wind_text}:* `{wind_kph} {kph_text}`*💧 {humidity_text}:* `{humidity}%`\n"
            f"*🌬 {pressure_text}:* `{pressure_mb} {mmhg_text}`\n\n"
            f"{rain_line}{snow_line}"
        )
        await message.answer(weather_message)
    else:
        await message.answer(template[lang]['no_such_city'])
        return


@router.callback_query(F.data == 'add_hour')
async def hours_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await callback.answer()
    await callback.message.edit_text(template[lang]['choose_hour'], reply_markup=await kb.hours_menu(lang))


@router.callback_query(F.data.startswith('hour_'))
async def set_notify(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    hour = int(callback.data.split('_')[1])
    await rq.add_notify(user_id, hour)
    await callback.answer(template[lang]['added'])


@router.callback_query(F.data.startswith('del_hour_'))
async def delete_notify(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    hour = callback.data.split('_')[2]
    await rq.delete_notify(user_id, hour)
    await callback.answer(template[lang]['deleted'])
    await callback.message.edit_text(template[lang]['notify_menu'], reply_markup=await kb.my_notif_menu(user_id, lang))


@router.callback_query(F.data == 'back_to_notify')
async def back_to_notify_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await callback.answer()
    await callback.message.edit_text(f"{template[lang]['notify_menu']}",
                                     reply_markup=await kb.my_notif_menu(user_id, lang))


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_session(user_id)
    lang = user['language']
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(template[lang]['main'], reply_markup=await kb.main_menu(lang))


@router.callback_query(F.data == 'noop')
async def noop_handler(callback: CallbackQuery):
    await callback.answer()
