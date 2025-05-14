import asyncio

import requests as rq
import api_clients as client
from sessions import get_session
from template import template

from datetime import datetime, timedelta


async def send_notifications(bot):
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    seconds_until_next_hour = int((next_hour - now).total_seconds())
    await asyncio.sleep(seconds_until_next_hour)
    while True:
        hour = datetime.now().hour
        notifies = await rq.get_notifies(hour)

        for notify in notifies:
            user_id = notify.user_id
            user = await get_session(user_id)
            lang = user['language']
            current = await client.current(user['location'])
            today = await client.today(user['location'])

            text = current['current']['condition']['text'].strip().lower()
            wind_kph = current['current']['wind_kph']
            humidity = current['current']['humidity']
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
            await bot.send_message(user_id, weather_message)
        await asyncio.sleep(3600)
