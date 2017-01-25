import datetime
import collections
import time
import urllib.request

import telepot
from icalendar import Calendar

try:
    bot = telepot.Bot('<key>')
except telepot.exception.BadHTTPResponse:
    pass


def handle(message):
    sender = message['chat']['id']

    if not message or not 'text' in message or message['text'][:8] != '/termine':
        return

    response = ''

    with urllib.request.urlopen(
            'https://calendar.google.com/calendar/ical/fjpgn5j13u5fja420lvpm48h14%40group.calendar.google.com/public/basic.ics') as ics:
        cal = Calendar.from_ical(ics.read())

        events = {}

        for component in cal.walk():
            if component.name != 'VEVENT':
                continue

            date = component.get('dtstart').dt
            summary = component.get('summary')

            if date not in events:
                events[date] = []

            events[date].append(summary)

        events = collections.OrderedDict(sorted(events.items()))

        today = datetime.datetime.now()

        for date in events:
            if date < today.date():
                continue

            if date == today.date() and today.time() > datetime.time(17):
                continue

            response += '*Aufgaben für den {}*'.format(date.strftime('%d.%m.%Y'))

            for event in events[date]:
                response += '\n- {}'.format(event).replace('_', '\\_').replace('*', '\\*')

            break

    bot.sendMessage(sender, response, parse_mode='Markdown')


bot.message_loop(handle)

while 1:
    time.sleep(10)

