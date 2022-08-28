"""
Парсинг дамп ответа социальной сети ВКонтакте на некоторый поисковый запрос.
"""

import json
from prettytable import PrettyTable


def get_profiles_and_groups():
    """
    Получает названия профилей и групп и их id
    """

    # Для каждого словаря: ключ - id, значение - screen_name
    profiles = {}
    groups = {}

    for profiles_info in data["profiles"]:
        profiles[profiles_info["id"]] = profiles_info["screen_name"]
    for group_info in data["groups"]:
        groups[group_info["id"]] = group_info["screen_name"]
    return profiles, groups


def updates_data(user_data, information):
    """
    Обновляет данные(суммирует лайки, репосты, просмотры, длину текста)
    """

    user_data[1:] = [x + y for x, y in zip(user_data[1:], information[1:])]
    return user_data


def parses_data():
    """
    Парсит данные json - запроса
    """

    users_data = {}
    profiles, groups = get_profiles_and_groups()

    # Пробегаемся по каждой записи
    for item in data["items"]:

        # Смотрим отправителя записи и его screeen_name
        from_id = item["from_id"]
        sender = profiles[from_id] if from_id > 0 else groups[abs(from_id)]

        # Полная информация о записи
        information_about_item = [
            sender,
            len(item["text"]),
            item["likes"]["count"],
            item["reposts"]["count"],
            item["views"]["count"],
        ]

        # Если это первый пост текущего пользователя, то добавляем
        if from_id not in users_data:
            users_data[from_id] = information_about_item
        else:
            users_data[from_id] = updates_data(
                users_data[from_id], information_about_item
            )

    # Сортируем по количеству просмотров по убыванию
    users_data = dict(
        sorted(users_data.items(), key=lambda x: x[1][-1], reverse=True)[:20]
    )
    return users_data


with open("search_posts.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Парсим данные запроса
users_info = parses_data()

# Создаём таблицу, добавляем заголовки
table = PrettyTable()
table.field_names = ["name", "id", "text", "likes", "reposts", "views"]
table.align["name"] = "l"

for user_id in users_info:
    users_info[user_id].insert(1, user_id)

    # Добавляем в таблицу новую строку
    table.add_row(users_info[user_id])
print(table)
