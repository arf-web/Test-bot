"""
more.py ежеминутно опрашивает Twitch API (v5) на наличие он-лайн стримов.
Список стримов формируется из name_id.json, который хранит
отслеживаемые каналы всех пользователей.
Ещё здесь текстовые шаблоны и функции
"""

from time import sleep
import json
from twitch import TwitchClient
from datetime import timedelta, datetime
import datetime

client = TwitchClient(client_id='YOUR_TOKEN')
minute = datetime.timedelta(0, 30, 0, 0, 3, 0)  # (day, sec, .00000*, .00*, min, hour)


tmp_welcome = f"""Я отправляю уведомления о начале стрима.
Чтобы отслеживать канал, отправь команду типа "добавить LIRIK"."""
tmp_notifier_on = f"""Теперь вы получаете уведомления о старте трансляции. 
Вы всегда можете остановить их и вернуться в меню."""
tmp_notifier_off = "Уведомления остановлены."
tmp_but_add = "Добавить канал"
tmp_but_off = "Выключить уведомления"
tmp_but_favs = "Мои каналы"
tmp_but_online = "Кто онлайн?"
tmp_but_remove = "Удалить канал"


# функция-конвертер для корректной интерпретации даты получаемой из API в JSON
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def get_key(d, value):
    # возвращает имя ключа по имени значения (value) из переданного словаря (d)
    for key, value in d.items():
        if value == value:
            return key


def get_names_id():
    # распаковывает name_id.json из списка в обычный словарь
    with open("name_id.json", "r") as name_id:
        return json.load(name_id)[0]


def get_lives():
    # возвращает live_channels.json из списка в обычный словарь
    with open("live_channels.json", "r") as live_channels:
        return json.load(live_channels)


if __name__ == "__main__":
    print("запуск из интерпретатора, детка")
    while True:

        # создание json с активными каналами
        with open("name_id.json", "r") as name_id:
            dict_json = json.load(name_id)[0]                       # чтение json и вывод из списка

        all_ids = set()                                             # вывод всех id каналов в множество
        for user in dict_json:
            for key in dict_json[user]:
                all_ids.add(dict_json[user][key])

        all_ids = list(all_ids)                                     # id каналы из множества в лист
        ids = ",".join(str(id) for id in all_ids)                   # объединение в строку с запятыми (для функции)

        streams = client.streams.get_live_streams(ids)              # получаем json по каждому стримящему каналу из ID

        with open("live_channels.json", "w") as live_dict:          # запись обратно в файл
            json.dump(streams, live_dict, indent=4, sort_keys=True, default=myconverter)

        sleep(61)


