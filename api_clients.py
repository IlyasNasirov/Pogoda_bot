import aiohttp
import os

API_KEY = os.getenv("API_KEY")
BASE_URL = "http://api.weatherapi.com/v1/{}.json"


async def current(q):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL.format('current'), params={'key': API_KEY, 'q': q}) as response:
            if response.status == 200:
                return await response.json()
            else:
                data = await response.json()
                return f"Error, code: {data}"


async def today(q):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL.format('forecast'), params={'key': API_KEY, 'q': q, 'days': 2}) as response:
            if response.status == 200:
                data = await response.json()
                return data['forecast']['forecastday'][0]
            else:
                data = await response.json()
                return f"Error, code: {data}"


async def tomorrow(q):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL.format('forecast'), params={'key': API_KEY, 'q': q, 'days': 2}) as response:
            if response.status == 200:
                data = await response.json()
                return data['forecast']['forecastday'][1]
            else:
                data = await response.json()
                return f"Error, code: {data}"


async def forecast(q, days):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL.format('forecast'), params={'key': API_KEY, 'q': q, 'days': days}) as response:
            if response.status == 200:
                return await response.json()
            else:
                data = await response.json()
                return f"Error, code: {data['code']}"


async def get_city(q):
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL.format('current'), params={'key': API_KEY, 'q': q}) as response:
            if response.status == 200:
                data = await response.json()
                return data['location']['name']
            else:
                data = await response.json()
                return f"Error, code: {data['error']['code']}"
