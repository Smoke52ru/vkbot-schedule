"""Модели, связанные с работой бота, скоро добавятся новые, пока так"""
from datetime import datetime
from pony.orm import *

# TODO в конфиг
DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    password='VKschedulebotpassword',
    host='localhost',
    database='vk_schedule_bot')

db = Database()
db.bind(**DB_CONFIG)


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    chat_id = Required(int)
    name = Optional(str, 255)
    mail = Required('Mail')
    schedule = Required('Schedule')
    trial = Required('Trial')
    active = Required(bool)


class Trial(db.Entity):
    id = PrimaryKey(int, auto=True)
    is_active = Optional(bool)
    over = Optional(datetime)
    group = Optional(Group)


class Schedule(db.Entity):
    id = PrimaryKey(int, auto=True)
    login = Optional(str, 255)
    password = Optional(str, 255)
    group = Optional(Group)


class Mail(db.Entity):
    id = PrimaryKey(int, auto=True)
    host = Optional(str, 255)
    login = Optional(str, 255)
    password = Optional(str, 255)
    group = Optional(Group)


db.generate_mapping(create_tables=True)
