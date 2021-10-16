import time
from email import header
from imaplib import IMAP4_SSL
import email


class MailParser:
    MAIL_COUNT = None
    # TODO Темыч, здесь данные можешь перенести в config.py, чтобы никто
    #  не видел(я про 'user')
    CONNECTION_DATA = {'host': "imap.mail.ru",
                       'port': 993,
                       'user': {'user': 'pri19.19.1@mail.ru',
                                'password': 'platoff42'}}

    def __init__(self):
        self.connection = IMAP4_SSL(host=self.CONNECTION_DATA['host'],
                                    port=self.CONNECTION_DATA['port'])
        self.connection.login(**self.CONNECTION_DATA['user'])
        self.MAIL_COUNT = self.get_mail_count()

    def get_mail_count(self):
        return int(self.connection.select('INBOX')[1][0])

    def get_last_mails(self, count):
        mails = []
        typ, data = self.connection.search(None)

        for num in data[0].split()[-count:]:
            typ, message_data = self.connection.fetch(num, '(RFC822)')
            for response_part in message_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    mails.extend(["\n".join(f"{header.upper():8}: "
                                            f"{self.decode_header(msg[header] if msg[header] else 'Пустой заголовок')}"
                                            for header in
                                            ['subject', 'to', 'from'])])
        return "\n".join(mails)

    def check(self):
        """
        Функция проверки появления новых сообщений
        Сравнивает количество текущих письм на почте, с тем, что было до этого
        :return: Заголовок, отправитель, принимающий новыйх писем
        """
        mail_count = self.get_mail_count()
        if mail_count > self.MAIL_COUNT:
            new_mails_count = mail_count - self.MAIL_COUNT

            self.MAIL_COUNT = mail_count
            return self.get_last_mails(new_mails_count)

        return None

    @staticmethod
    def decode_header(headerMsg):
        """
        Не ебу как это работает, потому что заебался разбираться с кодировками в этой ебаной библиотеке, функцию
        спиздив с интернета
        :param headerMsg: строка, которую нужно декодировать
        :return: декодированная строка
        """
        L = header.decode_header(headerMsg)
        s = ''
        for s1, chset in L:
            if isinstance(s1, bytes):
                s += s1.decode(chset) if chset else s1.decode()
            else:
                s += s1
        return s


if __name__ == '__main__':
    parser = MailParser()
    print(parser.check())
    time.sleep(60)
    print(parser.check())