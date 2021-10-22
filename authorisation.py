"""Модуль регистрации бота и работы с его данными"""
import datetime
from datetime import timedelta
import re
from imaplib import IMAP4_SSL
import requests
from bs4 import BeautifulSoup
from models import *


class AuthenticationHandlers:

    @staticmethod
    def get_mail_host(mail):
        """
        Функция, генерирующая host, из имени почты
        :param mail: почта
        :return: host
        """
        return "imap." + re.findall(r'@([a-z.]*)', mail)[0]

    def mail(self, login, password):
        """
        Хэндлер проверки правильности данных для почты
        :param login: логин
        :param password: пароль
        :return: Ture - если пара login, password верны, False - если нет
        """
        try:
            connection = IMAP4_SSL(host=self.get_mail_host(login), port=993)
            connection.login(user=login, password=password)
        except Exception as exc:
            return False
        return True

    @staticmethod
    def schedule(login, password):
        """
        Хэндлер проверки правильности данных для расписания
        :param login: логин
        :param password: пароль
        :return: Ture - если пара login, password верны, False - если нет
        """
        url = 'https://www.nngasu.ru/cdb/schedule/student.php?login=yes'
        auth_dict = {
            'AUTH_FORM': 'Y',
            'TYPE': 'AUTH',
            'USER_LOGIN': login,
            'USER_PASSWORD': password,
            'backurl': '\\cdb\\schedule\\student.php',
            'Login': 'Войти'
        }

        response = requests.post(url=url, data=auth_dict, proxies={'http': 'http://proxy.server:3128'})
        return BeautifulSoup(response.text, 'lxml').find('iframe') is not None


class ChatAuthentication:

    def __init__(self):
        self.handler = AuthenticationHandlers()

    @db_session
    def registration(self, registration_data: str, chat_name: str, chat_id: int):
        """
        Фукнция регистрации бота :param registration_data: строка, присланная от пользователя в формате:
        '/reg schedule_login schedule_password mail_login mail_password'
        :param chat_name: имя чата
        :param chat_id: id беседы, для которого создается бот
        :return: строка - ответ пользователю
        """
        data = registration_data.split()[1:]
        schedule_data, mail_data = data[:2], data[2:]
        if not self.handler.schedule(*schedule_data):
            return 'Не удалось подключиться к расписанию! Проверьте правильность вводимых данных'
        if not self.handler.mail(*mail_data):
            return 'Не удалось подключиться к почте! Проверьте правильность вводимых данных'

        if select(group for group in Group if group.chat_id == chat_id).exists():
            return 'Бот для вашей беседы уже был зарегистрирован!'

        self.registration_models_create(schedule_data, mail_data, chat_name, chat_id)
        return 'Регистрация бота прошла успешно!'

    @db_session
    def update(self, update_string: str, chat_id):
        """
        Функция обновления данных по почте или расписанию
        :param update_string: строка, присланная от пользователя в формате:
        '/update schedule login password\n' или '/update mail login password'
        :param chat_id: id беседы
        :return: строка - ответ пользователю
        """
        data = update_string.split()[1:]
        argument, login, password = data[:3]

        if argument not in ('schedule', 'mail'):
            return 'Проверьте правильность вводимой команды! Она должна иметь вид:\n' \
                   '/update schedule login password\n' \
                   '/update mail login password'

        handler = getattr(AuthenticationHandlers, argument)
        if handler(login, password):
            self.update_models(chat_id, argument, login, password)
            return 'Данные успешно обновлены!'

        return 'Не удалось обновить данные о почте! Проверьте правильность вводимых данных!'

    def registration_models_create(self, schedule_data, mail_data, chat_name, chat_id):
        """
        Функция создания новых записей в бд при регистрации бота
        :param schedule_data: список в формате ['schedule_login', 'schedule_password']
        :param mail_data: список в формате ['mail_login', 'mail_password']
        :param chat_name: название беседы
        :param chat_id: id беседы
        """
        schedule = Schedule(login=schedule_data[0], password=schedule_data[1])
        mail = Mail(host=self.handler.get_mail_host(mail_data[0]), login=mail_data[0], password=mail_data[1])
        trial = Trial(is_active=True, over=datetime.now() + timedelta(days=7))
        group = Group(chat_id=chat_id, name=chat_name, mail=mail, schedule=schedule, trial=trial)
        commit()

    def update_models(self, chat_id, argument, login, password):
        """
        Функция обновления записей в бд
        :param chat_id: id беседы
        :param argument: 'mail' или 'schedule'
        :param login: новый логин
        :param password: новый пароль
        """
        group = select(group for group in Group if group.chat_id == chat_id).get()
        attr = getattr(group, argument)

        attr.login = login
        attr.password = password
        if argument == 'mail':
            attr.host = self.handler.get_mail_host(login)
        commit()


if __name__ == '__main__':
    update_schedule_string = '/update schedule login password'
    update_mail_string = '/update mail login password'
    reg_string = '/reg gr_PRI19.19-1 ev6eaa pri19.19.1@mail.ru platoff42'
