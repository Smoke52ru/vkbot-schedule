"""Модуль админки, пока простейшей"""
from models import *
from pony.orm import *


class BotAdminApi:

    @db_session
    def ban_chat(self, chat_id):
        """
        Фукнция отключения работы бота, для определенной беседы
        :param chat_id: id беседы
        :return: строка ответа пользователю
        """
        chat = self.get_chat_by_id(chat_id)
        chat.active = False

        commit()
        return f'Беседа с id {chat_id} успешно заблокирована!'

    @db_session
    def unban_chat(self, chat_id):
        """
        Фукнция включения работы бота, для определенной беседы
        :param chat_id: id беседы
        :return: строка ответа пользователю
        """
        chat = self.get_chat_by_id(chat_id)
        chat.active = True

        commit()
        return f'Беседа с id {chat_id} успешно разблокирована!'

    @db_session
    def remove_free_trial(self, chat_id):
        """
        Фукнция отключения бесплатного периода для беседы, (после того как бесплатный период заканчивается,
        бот автоматически перестает работать, для того чтобы он снова функционировал, необходимо отключить
        бесплатный период, делается это после оплаты пользователем)
        :param chat_id: Номер
        """
        chat = self.get_chat_by_id(chat_id)
        chat.trial.is_active = False

        commit()
        return f'Бесплатный период для беседы с id {chat_id} отключен успешно'

    @staticmethod
    def get_chat_by_id(id):
        """
        Фукнция получения данных бота для беседы с номером == id, из базы данных
        :param id: id беседы
        :return: запись из бд
        """
        return select(group for group in Group if group.chat_id == id).get()

