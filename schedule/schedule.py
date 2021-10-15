"""
    Import:
        from schedule import Schedule
    Use:
        today_schedule          =   Schedule()
        one_day_schedule        =   Schedule('date')
        several_days_schedule   =   Schedule('start_date', 'end_date')
"""
import requests
from bs4 import BeautifulSoup
try:
    from schedule.config import NNGASU_LOGIN, NNGASU_PASSWORD
except Exception:
    import os
    NNGASU_LOGIN = os.environ.get('NNGASU_LOGIN')
    NNGASU_PASSWORD = os.environ.get('NNGASU_PASSWORD')


class Schedule:
    # authorization link
    _url_login = \
        'https://www.nngasu.ru/cdb/schedule/student.php?login=yes'

    def __init__(self,
                 _start_date='',
                 _end_date='',
                 clean_dublicates_flag=True):
        # result list of lessons
        self.raw_list_of_lessons = list()
        # auth dict is required for the POST request
        self.auth_dict = \
            {
                'AUTH_FORM': 'Y',
                'TYPE': 'AUTH',
                'USER_LOGIN': NNGASU_LOGIN,
                'USER_PASSWORD': NNGASU_PASSWORD,
                'backurl': '\\cdb\\schedule\\student.php',
                'Login': 'Войти'
            }

        # initializing date range for request
        self.start_date = _start_date
        self.end_date = _start_date if _end_date == '' else _end_date
        # authorizing
        _response = requests.post(url=Schedule._url_login,
                                  data=self.auth_dict,
                                  proxies={'http': 'http://proxy.server:3128'})
        _iframe = BeautifulSoup(_response.text, 'lxml').find('iframe')
        if _iframe is None:
            print('Ошибка авторизации')
        # getting link to schedule and adding parameters
        self._url_schedule = str(_iframe.get('src'))
        self._url_schedule = self.add_date_to_request(self.start_date,
                                                      self.end_date)
        # getting schedule <table>
        _response = requests.get(self._url_schedule)
        self._unparsed_tab = BeautifulSoup(_response.text, 'lxml').find('table')

        # parsing of schedule table
        self.parsing()
        if clean_dublicates_flag:
            self.result_list_of_lessons = self.clean_raw_list_from_dublicates()

    def add_date_to_request(self, start_date='', end_date=''):
        if start_date != '':
            self._url_schedule += f'&ScheduleSearch%5Bstart_date%5D={start_date}'
        if end_date != '':
            self._url_schedule += f'&ScheduleSearch%5Bend_date%5D={end_date}'
        return self._url_schedule

    def parsing(self):
        # parsing of schedule table
        rows = self._unparsed_tab.find_all('tr')
        for tr in rows[1:]:
            # получаем ссылку на конференцию(если есть)
            try:
                link = tr.find('a').get('href')
            except Exception:
                link = None
            # получаем пары(уроки)
            lesson = list()
            for td in tr.contents[1::2]:
                # if td != '\n' and td.string is not None:
                cell = str(td.string).strip()
                if cell == 'None':
                    cell = ''
                lesson.append(cell)
            # записываем ссылку
            if link is not None:
                lesson.append(str(link))
            # записываем пару
            self.raw_list_of_lessons.append(lesson)

    def clean_raw_list_from_dublicates(self):
        # очистка дубликатов (то же время, тот же препод)
        result = self.raw_list_of_lessons[0:1]
        for cur_lesson in self.raw_list_of_lessons[1:]:
            if cur_lesson[0] == result[-1][0] and cur_lesson[1] == result[-1][1] and cur_lesson[3] == result[-1][3]:
                result[-1][4] += f', {cur_lesson[4]}'
            else:
                result.append(cur_lesson)
        return result

    # TODO
    def nngasu_authorize(self):
        pass

    def __str__(self):
        res = str()
        for lst in self.result_list_of_lessons:
            for i in lst:
                if str(i) != '':
                    res += str(i) + '\n'
            res += '\n'
        return res


if __name__ == '__main__':
    today = '07.09.2021'
    schedule = Schedule(today)
    print(f'{schedule._url_schedule=}')
    print(schedule.__str__())
