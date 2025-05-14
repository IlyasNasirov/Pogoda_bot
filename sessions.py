import asyncio

from datetime import datetime, timedelta

import requests as rq

SESSION_TTL = timedelta(hours=6)
active_sessions = {}


async def set_session(id, location=None, language=None):
    if id not in active_sessions:
        active_sessions[id] = {}
    if location is not None:
        active_sessions[id]['location'] = location
        await rq.save_location(id, location)
    if language is not None:
        active_sessions[id]['language'] = language
        await rq.set_language(id, language)


async def get_session(id):
    exist = active_sessions.get(id)
    if not exist:
        user = await rq.get_user(id)
        active_sessions[id] = {
            'location': user.location,
            "language": user.language
        }
    active_sessions[id]['last_access'] = datetime.now()
    return active_sessions.get(id)


async def clear_expired_sessions():
    while True:
        now = datetime.now()
        expired_ids = [
            user_id for user_id, data in active_sessions.items()
            if now - data.get("last_access", now) > SESSION_TTL
        ]
        for user_id in expired_ids:
            del active_sessions[user_id]
        await asyncio.sleep(7200)
