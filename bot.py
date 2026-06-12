import os
import telebot
import requests
import json

# Загрузка токена и API-ключа из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
API = os.getenv('OPENWEATHER_API_KEY')

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Добро пожаловать в бот погоды!\n\nНапишите название города, чтобы узнать текущую погоду.\n\nПримеры: Москва, London, Paris'
    )


@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()

    # Отправляем сообщение о том, что бот думает
    bot.send_message(message.chat.id, f'Ищу погоду в городе {city.title()}...')

    try:
        res = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric',
            timeout=10
        )

        if res.status_code == 200:
            data = json.loads(res.text)
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            weather_desc = data["weather"][0]["description"]

            # Формируем красивое сообщение
            weather_text = (
                f'Город: {city.title()}\n'
                f'Температура: {temp}°C\n'
                f'Ощущается как: {feels_like}°C\n'
                f'Влажность: {humidity}%\n'
                f'Ветер: {wind_speed} м/с\n'
                f'Описание: {weather_desc.capitalize()}'
            )

            bot.send_message(message.chat.id, weather_text)

            # Отправляем картинку в зависимости от температуры
            if temp > 20:
                image = 'sun.jpg'
                caption = 'Тепло! Можно идти гулять!'
            elif temp > 5:
                image = 'cloudy.jpg'
                caption = 'Прохладно, лучше надеть куртку'
            else:
                image = 'rainy.png'
                caption = 'Холодно! Одевайтесь теплее!'

            # Проверяем, существует ли файл с картинкой
            try:
                file = open(f'./{image}', 'rb')
                bot.send_photo(message.chat.id, file, caption=caption)
            except FileNotFoundError:
                bot.send_message(message.chat.id, caption)

        elif res.status_code == 404:
            bot.send_message(
                message.chat.id,
                f'Город "{city.title()}" не найден.\nПроверьте название и попробуйте снова.'
            )
        else:
            bot.send_message(
                message.chat.id,
                'Что-то пошло не так. Попробуйте позже.'
            )

    except requests.exceptions.Timeout:
        bot.send_message(message.chat.id, 'Сервер погоды не отвечает. Попробуйте позже.')
    except requests.exceptions.ConnectionError:
        bot.send_message(message.chat.id, 'Нет подключения к интернету. Проверьте соединение.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')


if __name__ == '__main__':
    print('Бот погоды запущен...')
    print('Команды: /start')
    bot.polling(none_stop=True)
