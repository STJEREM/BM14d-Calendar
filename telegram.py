import datetime
import collections
import time
import os
import urllib.request
import telepot
import json
from icalendar import Calendar

try:
    bot = telepot.Bot(os.environ['TELEGRAM_API_KEY'])
except telepot.exception.BadHTTPResponse:
    exit(1)

me = bot.getMe()


def handle(message):
    events = {}
    today = datetime.datetime.now()

    message['to'] = me

    with open('/var/log/bm14d-bot/messages.log', 'a') as file:
        file.write(json.dumps(message) + '\n')

    sender = message['chat']['id']

    if not message or not 'text' in message or message['text'][:8] != '/termine':
        return

    with urllib.request.urlopen(
            'https://calendar.google.com/calendar/ical/fjpgn5j13u5fja420lvpm48h14%40group.calendar.google.com/public/basic.ics') as ics:
        cal = Calendar.from_ical(ics.read())

        for component in cal.walk():
            if component.name != 'VEVENT':
                continue

            date = component.get('dtstart').dt
            summary = component.get('summary')

            if date < today.date() or (date == today.date() and today.time() > datetime.time(17)):
                continue

            if date not in events:
                events[date] = []

            events[date].append(summary)

    events = collections.OrderedDict(sorted(events.items()))

    response = '\n\n'.join([format_day(day, events) for day in events])
    sent_message = bot.sendMessage(sender, response, parse_mode='Markdown')

    try:
        bot.pinChatMessage(sent_message['chat']['id'], sent_message['message_id'], disable_notification=True)
    except:
        pass


def format_day(day, events):
    response = '*Aufgaben für den {}*'.format(day.strftime('%d.%m.%Y'))

    for event in events[day]:
        response += '\n- {}'.format(event).replace('_', '\\_').replace('*', '\\*')

    return response


bot.message_loop(handle)

while 1:
    time.sleep(10)
