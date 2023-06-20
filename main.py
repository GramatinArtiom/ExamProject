from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
import os
from dotenv import load_dotenv
import datetime
import pyjokes
import qrcode
import requests
from collections import defaultdict
import random

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)
accounts = defaultdict(float)

mainCommands = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
mainCommands.add('QR code generator').add('Music').add("Weather").add('Current time').add('Joke').add("Finance").add(
    "Movies")
finance = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
finance.add("/income").add("/expense").add("/balance").add("/over")

nickname = ""
generate_qr_flag = False
income_flag = False
expense_flag = False
movie_search_flag = False
music_search_flag = False
weather_flag = False
omdb_api_key = str(os.getenv('OMDB_API_KEY'))
spotify_api_key = str(os.getenv('SPOTIFY_API_KEY'))



@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    global nickname
    nickname = f"{message.from_user.first_name}_{message.from_user.last_name}"
    await message.answer(f"Hello {nickname}, to continue type '/maincommands'")


@dp.message_handler(commands=["maincommands"])
async def mainCommandsFunction(message: types.Message):
    global nickname
    await message.answer(f"{nickname}, these are the main commands.", reply_markup=mainCommands)


@dp.message_handler(text=['Current time'])
async def get_current_time(message: types.Message):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    await message.answer(f"The current time is: {current_time}, anything else?", reply_markup=mainCommands)


@dp.message_handler(text=['Joke'])
async def generate_joke(message: types.Message):
    joke = pyjokes.get_joke()
    await message.answer(f"{joke} I hope you laughed a little! Anything else?", reply_markup=mainCommands)


@dp.message_handler(text=['QR code generator'])
async def generate_qr_command(message: types.Message):
    global generate_qr_flag
    generate_qr_flag = True
    await message.answer("Type below what you want to generate.")


@dp.message_handler(text=['Finance'])
async def command_Start_Finance(message: types.Message):
    global nickname
    user_id = message.from_user.id
    if user_id not in accounts:
        accounts[user_id] = 0
    await message.answer(f"Ok {nickname}, you need to type '/income' if you want to register your income, "
                         f"type '/expense' for your expenses, '/balance' for your current balance and '/over' "
                         f"to finish the finance commands", reply_markup=finance)


@dp.message_handler(commands=['balance'])
async def command_balance(message: types.Message):
    user_id = message.from_user.id
    balance = accounts.get(user_id, 0)
    await message.answer(f"Your current balance: {balance} MDL", reply_markup=finance)
    print(balance)


@dp.message_handler(commands=['income'])
async def command_income(message: types.Message):
    global income_flag
    income_flag = True
    await message.answer("Enter the amount of the income.")


@dp.message_handler(commands=['expense'])
async def command_expense(message: types.Message):
    global expense_flag
    expense_flag = True
    await message.answer("Enter the amount of the expense.")


@dp.message_handler(commands=['over'])
async def command_over(message: types.Message):
    global income_flag, expense_flag
    income_flag = False
    expense_flag = False
    await message.answer("You finished the finance commands.", reply_markup=mainCommands)


@dp.message_handler(text=['Movies'])
async def command_start_movies(message: types.Message):
    global movie_search_flag
    movie_search_flag = True
    await message.answer("Enter the name of the movie you want to search:")


@dp.message_handler(text=['Music'])
async def command_start_music(message: types.Message):
    global music_search_flag
    music_search_flag = True
    await message.answer("Enter a keyword to search for a track:")


@dp.message_handler(text=['Weather'])
async def get_weather(message: types.Message):
    global weather_flag
    weather_flag = True
    await message.answer("Please enter a location for the weather forecast:")


@dp.message_handler()
async def echo_message(message: types.Message):
    global generate_qr_flag, income_flag, expense_flag, movie_search_flag, music_search_flag, weather_flag

    if generate_qr_flag:
        generate_qr_flag = False
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(message.text)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        img_path = f"qr_codes/{nickname}.png"
        img.save(img_path)
        await message.answer_photo(types.InputFile(img_path))
        os.remove(img_path)
        await message.answer("Here's your QR code! Anything else?", reply_markup=mainCommands)
        print(message)

    elif income_flag:
        try:
            income = float(message.text)
            user_id = message.from_user.id
            accounts[user_id] += income
            await message.answer(f"Income of {income} MDL registered. Anything else?", reply_markup=finance)
        except ValueError:
            await message.answer("Invalid input! Please enter a number for the income.")
        income_flag = False

    elif expense_flag:
        try:
            expense = float(message.text)
            user_id = message.from_user.id
            accounts[user_id] -= expense
            await message.answer(f"Expense of {expense} MDL registered. Anything else?", reply_markup=finance)
        except ValueError:
            await message.answer("Invalid input! Please enter a number for the expense.")
        expense_flag = False

    elif movie_search_flag:
        movie_search_flag = False
        movie_name = message.text
        global omdb_api_key

        response = requests.get(f"http://www.omdbapi.com/?t={movie_name}&apikey={omdb_api_key}")
        data = response.json()
        print(data)
        if data.get('Response') == 'True':
            title = data.get('Title', '')
            year = data.get('Year', '')
            plot = data.get('Plot', '')
            rating = data.get('imdbRating', '')
            imdb_link = data.get('imdbID', '')
            if imdb_link:
                imdb_link = f"https://www.imdb.com/title/{imdb_link}"
            await message.answer(
                f"Title: {title}\nYear: {year}\nPlot: {plot}\nRating: {rating}\nIMDb Link: {imdb_link}\nAnything else?",
                reply_markup=mainCommands)
        else:
            await message.answer("No movies found. Anything else?", reply_markup=mainCommands)

    elif music_search_flag:
        music_search_flag = False
        keyword = message.text
        global spotify_api_key

        headers = {
            "Authorization": f"Bearer {spotify_api_key}"
        }
        response = requests.get(f"https://api.spotify.com/v1/search?q={keyword}&type=track,playlist", headers=headers)
        data = response.json()
        print(data)
        if 'tracks' in data and 'items' in data['tracks'] and data['tracks']['items']:
            track = random.choice(data['tracks']['items'])
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            track_url = track['external_urls']['spotify']
            await message.answer(f"Track: {track_name}\nArtist: {artist_name}\nURL: {track_url}\nAnything else?",
                                 reply_markup=mainCommands)
        else:
            await message.answer("No track found. Anything else?", reply_markup=mainCommands)

    elif weather_flag:
        location = message.text

        url = f'https://api.weatherapi.com/v1/current.json?key=3dfed9f80ef645f58f9184555231306&q={location}'

        response = requests.get(url)
        data = response.json()
        print(data)
        if response.status_code == 200:
            temperature = data['current']['temp_c']
            condition = data['current']['condition']['text']
            humidity = data['current']['humidity']
            wind_speed = data['current']['wind_kph']

            weather_info = f"Weather in {location}:\nTemperature: {temperature}°C\nCondition: {condition}\n" \
                           f"Humidity: {humidity}%\nWind Speed: {wind_speed} km/h"

            await message.answer(weather_info, reply_markup=mainCommands)
        else:
            await message.answer("Failed to retrieve weather data. Please try again.", reply_markup=mainCommands)

        weather_flag = False

    else:
        await message.answer("I'm sorry, I didn't understand that command. Please choose a command from the keyboard.",
                             reply_markup=mainCommands)

print(accounts)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
