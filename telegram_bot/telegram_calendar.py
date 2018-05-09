import calendar
from datetime import datetime
from telebot import types

from telegram_bot import button_titles


class TelegramCalendar(object):

    def __init__(self):
        self.__current_shown_dates = {}

    @property
    def current_shown_dates(self):
        return self.__current_shown_dates

    def __create_calendar(self, year, month) -> object:
        '''
        Function creates keyboard markup for telegram bot.

        :param int year: year for markup creation.
        :param int month: month for markup creation.
        :return object: returns ReplyMarkupKeyboard object.
        '''
        markup = types.ReplyKeyboardMarkup()
        # First row - Month and Year
        markup.row(button_titles.PREVIOUS, calendar.month_name[month] + ' ' + str(year), button_titles.NEXT)
        # Second row - Week Days
        week_days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        row = []
        for day in week_days:
            row.append(day)
        markup.row(*row)

        my_calendar = calendar.monthcalendar(year, month)
        for week in my_calendar:
            row = []
            for day in week:
                if(day == 0):
                    row.append(' ')
                else:
                    row.append(str(day))
            markup.row(*row)
        # Last row - Buttons
        markup.row(button_titles.CANCEL)
        return markup

    def date_validation(self, value: type) -> bool:
        '''
        Function validates input date value. Returns True if validation successful, False if not.

        :param type value: value for validation.
        :rtype: bool.
        '''
        try:
            if int(value) > 0 and int(value) <= 31:
                return True
            else:
                return False
        except ValueError:
            return False

    def calendar_today(self, message: object) -> object:
        '''
        Function creates calendar markup which based on the current month.

        :param object message: message object.
        :rtype: ReplyKeyboardMarkup.
        '''
        now = datetime.now()
        chat_id = message.chat.id
        date = (now.year, now.month)
        self.__current_shown_dates[chat_id] = date
        markup = self.__create_calendar(now.year, now.month)
        return markup

    def calendar_next_month(self, message: object) -> object:
        '''
        Function creates calendar markup for next month which based on the `self.__current_shown_dates` variable.

        :param object message: message object.
        :rtype: ReplyKeyboardMarkup.
        '''
        chat_id = message.chat.id
        saved_date = self.__current_shown_dates.get(chat_id)
        if(saved_date is not None):
            year, month = saved_date
            month += 1
            if month > 12:
                month = 1
                year += 1
            date = (year, month)
            self.__current_shown_dates[chat_id] = date
            markup = self.__create_calendar(year, month)
            return markup
        else:
            # Do something to inform of the error
            pass

    def calendar_previous_month(self, message: object) -> object:
        '''
        Function creates calendar markup for previous month which based on the `self.__current_shown_dates` variable.

        :param object message: message object.
        :rtype: ReplyKeyboardMarkup.
        '''
        chat_id = message.chat.id
        saved_date = self.__current_shown_dates.get(chat_id)
        if(saved_date is not None):
            year, month = saved_date
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            date = (year, month)
            self.__current_shown_dates[chat_id] = date
            markup = self.__create_calendar(year, month)
            return markup
        else:
            # Do something to inform of the error
            pass
