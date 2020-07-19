import telebot
from time import sleep
import re
import json
from twitch import TwitchClient
from datetime import timedelta, datetime
from datetime import *
import datetime
from telebot import types
from more import *

bot = telebot.TeleBot("YOUR_TOKEN")
client = TwitchClient(client_id='YOUR_TOKEN')


# приветствие + кнопки + сохранение юзер ID
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.chat.id)
    print("запуск")
    # создание кнопок
    markup = types.ReplyKeyboardMarkup(row_width=1)
    but_add = types.KeyboardButton(tmp_but_add)
    but_fav = types.KeyboardButton(tmp_but_favs)
    but_online = types.KeyboardButton(tmp_but_online)
    but_remove = types.KeyboardButton(tmp_but_remove)

    # расстановка
    markup.row(but_fav, but_online)
    markup.row(but_add, but_remove)

    bot.send_message(message.chat.id, tmp_welcome,
                     reply_markup=markup)

    # этот участок кода создаёт словарь с пользователем, в его первый запуск бота
    with open("name_id.json", "r") as name_id:
        dict_json = json.load(name_id)[0]                           # импорт json + вывод его из списка
        if user_id not in dict_json: dict_json[user_id] = {}

    with open("name_id.json", "w") as name_id:                      # открываем то же документ уже для перезаписи
        json.dump([dict_json], name_id, indent=4, sort_keys=True)   # вносим обновлённый словарь


# кнопка добавления
@bot.message_handler(regexp=tmp_but_add)
def button_add(message):
    bot.send_message(message.chat.id, "Если хотите добавить канал, просто напишите об этом, например: Добавить LIRIK")


# добавление канала сразу в json и вывод имени
@bot.message_handler(regexp=r"Добавить \w{4}")
def channel_input(message):
    if len(message.text) <= 34:
        bot.send_message(message.chat.id, "Поиск канала на Twitch...")

        # Поиск ID по названию канала
        channel_name = re.sub(r"Добавить ", r"", message.text)  # просим ввести канал и запоминаем название
        search_result = client.search.channels(channel_name, limit=5)  # функция поиска возвращает каналы в json, запоминаем

        print(search_result)
        # Пользователь выбирает нужный канал ориентируясь на написание ника и кол-во фолловеров
        for channel in search_result:
            if channel["name"] == channel_name.lower():  # находим словарь с этим названием
                with open("name_id.json", "r") as name_id:  # открытие словаря с именами и ID для чтения
                    dict_json = json.load(name_id)[0]  # импорт json + вывод его из списка
                    dict_json[str(message.chat.id)].update({channel["display_name"]: channel["id"]})  # словарь обновляется новым содержимым
                    # (!) но записать его методом dump надо в внутри списка: [dict_json]

                with open("name_id.json", "w") as name_id:  # открываем то же документ уже для перезаписи
                    json.dump([dict_json], name_id, indent=4, sort_keys=True)  # вносим обновлённый словарь

                bot.send_message(message.chat.id, f"""Канал "{channel["display_name"]}" добавлен.""")
                break


# список каналов
@bot.message_handler(regexp=tmp_but_favs)
def show_list(message):
    dict_json = get_names_id()

    my_channels = "Вы отслеживаете: "
    for key, value in dict_json[str(message.chat.id)].items():
        my_channels += "\n" + key

    bot.send_message(message.chat.id, my_channels)


# кто онлайн
@bot.message_handler(regexp=tmp_but_online)
def who_online(message):
    dict_json = get_names_id()                                      # чтение json и вывод из списка

    fav_id_list = dict_json[str(message.chat.id)].values()          # достаём только ID каналов юзера

    streams = get_lives()                                           # достаём live_channels.json

    show_online = "Сейчас онлайн: "
    for active in streams:                                          # сравниваем ID массива с ID избранного
        if active["channel"]["id"] in fav_id_list:

            newtime = datetime.datetime.strptime(active["created_at"], "%Y-%m-%d %H:%M:%S")
            on_air = datetime.datetime.utcnow() - newtime
            on_air_hours, on_air_minutes = on_air.seconds // 3600, on_air.seconds // 60 % 60
            show_online += f"""\n twitch.tv/{active["channel"]["display_name"]} \n В эфире: {on_air_hours} ч. {on_air_minutes} мин., зрителей: {active["viewers"]} \n"""

    bot.send_message(message.chat.id, show_online, disable_web_page_preview=True)


# Кнопка удаления
@bot.message_handler(regexp=tmp_but_remove)
def button_remove(message):
    bot.send_message(message.chat.id, "Если хотите удалить канал, так же, напишите об этом, например: Удалить LIRIK")


# Удаление из списка каналов👍
@bot.message_handler(regexp=r"Удалить \w{4}")
def channel_delete(message):
    if len(message.text) <= 34:
        channel_name = re.sub(r"Удалить ", r"", message.text)                   # запоминаем имя удаляемого канала

        dict_json = get_names_id()

        if channel_name in dict_json[str(message.chat.id)]:
            dict_json[str(message.chat.id)].pop(channel_name)

            with open("name_id.json", "w") as name_id:                          # перезапись файла с именами
                json.dump([dict_json], name_id, indent=4, sort_keys=True)

            bot.send_message(message.chat.id, f"Вы больше не отслеживаете {channel_name}.")


bot.polling()
