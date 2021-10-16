import asyncio
from vkwave.bots import SimpleBotEvent, SimpleLongPollBot
from vkwave.bots.utils.keyboards import Keyboard
from schedule import Schedule
from mailparser import MailParser
from datetime import datetime, timedelta
import os

try:
    from schedule.config import TOKEN, GROUP_ID
except Exception:
    TOKEN = str(os.environ.get('TOKEN'))
    GROUP_ID = int(os.environ.get('GROUP_ID'))

GLOBAL_PREFIXES = ('/', '!', '', '@plato_v ')

HELP_COMMANDS = ('h', 'help')
SCHEDULE_COMMANDS = ('s', 'schedule', 'р', 'расписание')
KEYBOARD_COMMANDS = ('k', 'ks', 'keyboard')
HIDE_KEYBOARD_COMMANDS = ('hk', 'hide')
MAIL_PARSER_COMMANDS = ('почта', 'mail', 'm')

# bot init
bot = SimpleLongPollBot(tokens=TOKEN, group_id=GROUP_ID)

# mailparser init
mailparser = MailParser()


@bot.message_handler(bot.command_filter(commands=HELP_COMMANDS,
                                        prefixes=GLOBAL_PREFIXES))
async def help_command(event: SimpleBotEvent) -> str:
    return f"Hint: Боту можно писать в лс\n" \
           f"Prefixes: {GLOBAL_PREFIXES}\n" \
           f"\n" \
           f"Commands:\n" \
           f"h(elp) - список команд\n" \
           f"s(chedule) - сегодняшнее расписание\n" \
           f"s +[n] - расписание на n-ный день (напр. +1 - завтра)\n" \
           f"k - клавиатура с выбором дня недели\n" \
           f"hk - скрыть клавиатуру\n"


@bot.message_handler(bot.command_filter(commands=SCHEDULE_COMMANDS,
                                        prefixes=GLOBAL_PREFIXES))
async def schedule(event: SimpleBotEvent) -> str:
    args = event.text.split(' ')
    required_day = datetime.today()
    for arg in args:
        if arg[0] == '+':
            plus_days = int(arg[1:])
            required_day += timedelta(days=plus_days)

    return str(Schedule(required_day.strftime('%d.%m.%Y')))


#########################################################
#                     KEYBOARD                          #
#########################################################

KB_BUTTONS = (('пн', 'вт', 'ср', 'чт', 'пт'),
              ('сегодня', 'завтра'),
              ('почта',))

kb = Keyboard(one_time=False,
              inline=False)

for idx, button in enumerate(KB_BUTTONS[0]):
    kb.add_text_button(button,
                       payload={"schedule_option": button,
                                "day": idx})
kb.add_row()
for button in KB_BUTTONS[1]:
    kb.add_text_button(button,
                       payload={"schedule_option": button})

kb.add_row()
for button in KB_BUTTONS[2]:
    kb.add_text_button(button,
                       payload={"mail_option": button})


@bot.message_handler(bot.command_filter(commands=KEYBOARD_COMMANDS,
                                        prefixes=GLOBAL_PREFIXES))
async def get_keyboard_schedule(event: SimpleBotEvent):
    await event.answer(message='Ok',
                       keyboard=kb.get_keyboard())


@bot.message_handler(bot.payload_contains_filter(key="schedule_option"))
async def keyboard_schedule_handler(event: SimpleBotEvent):
    now = datetime.now()
    if event.payload["schedule_option"] == "сегодня":
        day = now
    elif event.payload["schedule_option"] == "завтра":
        day = now + timedelta(days=1)
    elif event.payload["schedule_option"] == "скрыть":
        await hide_keyboard_schedule(event)
        return
    else:
        day = now + timedelta(days=event.payload["day"] - now.weekday())

    answer = str(Schedule(day.strftime('%d.%m.%Y')))
    return answer


@bot.message_handler(bot.command_filter(commands=HIDE_KEYBOARD_COMMANDS,
                                        prefixes=GLOBAL_PREFIXES))
async def hide_keyboard_schedule(event: SimpleBotEvent):
    await event.answer(message='Ok',
                       keyboard=kb.get_keyboard())


#########################################################
#                         MAIL                          #
#########################################################

@bot.message_handler(bot.command_filter(commands=MAIL_PARSER_COMMANDS,
                                        prefixes=GLOBAL_PREFIXES)
                     | bot.payload_contains_filter("mail_option"))
async def mail_check(event: SimpleBotEvent):
    await event.answer(message=str(mailparser.check()))


#########################################################
#########################################################
#########################################################

# run bot
if __name__ == '__main__':
    # bot.run_forever()

    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())
    # loop.create_task(mailparser.run())
    loop.run_forever()
