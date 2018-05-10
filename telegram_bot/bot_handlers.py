from datetime import datetime

import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram_bot import button_titles
from telegram_bot.telegram_calendar import TelegramCalendar
from telegram_bot.limiter_helper import LimiterHelper
from config import telegram


bot = telebot.TeleBot(telegram['token'], threaded=False)
lhelper = LimiterHelper()
tcalendar = TelegramCalendar()


# Markups for /set_limit flow
def single_cancel_button_markup() -> object:
    '''
    Function returns markup with only one button '❌ Cancel'.

    :rtype: ReplyKeyboardMarkup.
    '''
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(button_titles.CANCEL)
    return markup


def set_category_markup() -> object:
    '''
    Function returns markup with all existing categories and '🆕 Add category' and '❌ Cancel' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    existing_categories = lhelper.get_categories()
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for entry in existing_categories:
        markup.row(entry)
    markup.row(button_titles.ADD_CATEGORY)
    markup.row(button_titles.CANCEL)
    return markup


def set_period_markup() -> object:
    '''
    Function returns markup with predefined periods and 'Another value', 'Select date', and '❌ Cancel' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(button_titles.DAY, button_titles.WEEK)
    markup.row(button_titles.MONTH, button_titles.YEAR)
    markup.row(button_titles.ANOTHER_VALUE, button_titles.SELECT_DATE)
    markup.row(button_titles.CANCEL)
    return markup


def yes_no_cancel_markup() -> object:
    '''
    Function returns markup with '✅ Yes', '❎ No', and '❌ Cancel' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(button_titles.YES, button_titles.NO)
    markup.row(button_titles.CANCEL)
    return markup


def accept_markup(accept_change_button=False) -> object:
    '''
    Function returns markup with '✅ Accept' and '❌ Cancel' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row(button_titles.ACCEPT)
    if accept_change_button:
        markup.row(button_titles.CHANGE)
    markup.row(button_titles.CANCEL)
    return markup


def get_limit_markup(limit: list) -> object:
    '''
    Function returns markup with all existing limits and '❌ Cancel' buttons.
    :rtype: ReplyKeyboardMarkup.
    '''
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for entry in limit:
        markup.row(entry['title'])
    markup.row(button_titles.CANCEL)
    return markup


# Helpers funcs for /set_limit flow
def cancel(message: object) -> None:
    '''
    Message response function on 'cancel_message'.

    :param object message: message object.
    :rtype: None.
    '''
    clr_keyboard = ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, '🔵 Canceled', reply_markup=clr_keyboard)


def set_limit_summary(message: object) -> None:
    '''
    Function sends message of summary of creating limit.

    :param object message: message object.
    :rtype: None.
    '''
    if lhelper.is_repeated:
        budget = 'On'
    else:
        budget = 'Off'
    text_off_message = '🔵 You are creating a limit\n'\
                       'Category: {category_name}\n'\
                       'Limit: {limit}\n'\
                       'Period: {period}\n'\
                       'Budget mode: {budget}\n'\
                       'Starts from: {start_date}\n'.format(category_name=lhelper.category_name,
                                                            limit=lhelper.limit,
                                                            period=lhelper.period,
                                                            start_date=lhelper.start_date.date(),
                                                            budget=budget)
    bot.send_message(message.chat.id, text_off_message, reply_markup=accept_markup())


def is_repeated_question(message: object) -> None:
    '''
    Function sends question message of repeating limit (budget mode).

    :param object message: message object.
    :rtype: None.
    '''
    bot.send_message(message.chat.id,
                     '🔵 You have set period (days): ' + str(lhelper.period) + '\n' +
                     '⚪️ Do you want to enable budget mode (repeating period)?',
                     reply_markup=yes_no_cancel_markup())


# Handlers for /set_limit flow
@bot.message_handler(commands=['set_limit'])
def set_limit(message: object) -> None:
    '''
    Handler for "/set_limit" command.

    :param object message: message object.
    :rtype: None.
    '''
    bot.send_message(message.chat.id, '⚪️ Choose category', reply_markup=set_category_markup())
    bot.register_next_step_handler(message, set_category_handler)


def set_category_handler(message: object) -> None:
    '''
    Handler for choosing `category_name`.
    This handler responds to clicks from `set_category_markup()` and determines the further
    flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    existing_categories = lhelper.get_categories()
    if message.text == button_titles.CANCEL:
        cancel(message)
    elif message.text == button_titles.ADD_CATEGORY:
        bot.send_message(message.chat.id, '⚪️ Enter name of category', reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, category_entered_value_handler)
    elif message.text in existing_categories:
        lhelper.category_name = message.text
        bot.send_message(message.chat.id,
                         '🔵 You selected category: ' + message.text + '\n' +
                         '⚪️ Enter limit value (UAH)',
                         reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, set_limit_value_handler)
    else:
        bot.send_message(message.chat.id, '🔴 Please select one of the menu items')
        bot.register_next_step_handler(message, set_category_handler)


def category_entered_value_handler(message: object) -> None:
    '''
    Handler for manual input of `category_name`.
    This handler responds to clicks from `single_cancel_button_markup()` and manual inputting of any text.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    else:
        lhelper.category_name = message.text
        bot.send_message(message.chat.id,
                         '⚪️ You are creating a limit for category: ' + message.text,
                         reply_markup=accept_markup(accept_change_button=True))
        bot.register_next_step_handler(message, category_accept_handler)


def category_accept_handler(message: object) -> None:
    '''
    Handler for manual input of `category_name`.
    This handler responds to clicks from `single_cancel_button_markup()` and manual inputting of any text.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    elif message.text == button_titles.CHANGE:
        bot.send_message(message.chat.id, '⚪️ Enter name of category', reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, category_entered_value_handler)
    elif message.text == button_titles.ACCEPT:
        bot.send_message(message.chat.id,
                         '🔵 You selected category: ' + lhelper.category_name + '\n' +
                         '⚪️ Enter limit value (UAH)',
                         reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, set_limit_value_handler)
    else:
        bot.send_message(message.chat.id, '🔴 Please select one of the menu items')
        bot.register_next_step_handler(message, category_accept_handler)


def set_limit_value_handler(message: object) -> None:
    '''
    Handler for manual input of `limit`.
    This handler responds and validates to manual inputting of limit.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    else:
        if lhelper.validate_limit(message.text):
            lhelper.start_date = datetime.utcnow()
            lhelper.limit = float(message.text)
            bot.send_message(message.chat.id,
                             '🔵 You have entered a limit: ' + message.text + '\n' +
                             '⚪️ Select a period',
                             reply_markup=set_period_markup())
            bot.register_next_step_handler(message, set_period_handler)
        else:
            bot.send_message(message.chat.id,
                             '🔴 The limit value must be a numeric value greater than zero',
                             reply_markup=single_cancel_button_markup())
            bot.register_next_step_handler(message, set_limit_value_handler)


def set_period_handler(message: object) -> None:
    '''
    Handler chosing `period`.
    This handler responds to clicks from `set_period_markup()` and manual inputting of any text.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    else:
        if message.text == button_titles.DAY:
            lhelper.period = 1
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == button_titles.WEEK:
            lhelper.period = 7
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == button_titles.MONTH:
            lhelper.period = 30
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == button_titles.YEAR:
            lhelper.period = 365
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == button_titles.ANOTHER_VALUE:
            bot.send_message(message.chat.id,
                             '⚪️ Enter the number of days that you want to set a limit',
                             reply_markup=single_cancel_button_markup())
            bot.register_next_step_handler(message, another_value_selected_handler)
        elif message.text == button_titles.SELECT_DATE:
            calendar_markup = tcalendar.calendar_today(message)
            bot.send_message(message.chat.id, '⚪️ Please, choose a date', reply_markup=calendar_markup)
            bot.register_next_step_handler(message, calendar_handler)
        else:
            bot.send_message(message.chat.id, '🔴 Please select one of the menu items')
            bot.register_next_step_handler(message, set_period_handler)


def another_value_selected_handler(message: object) -> None:
    '''
    Handler for manual input of `period`.
    This handler responds to clicks from `single_cancel_button_markup()` and validates manual inputting of period.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    else:
        if lhelper.validate_period(message.text):
            lhelper.period = int(message.text)
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        else:
            bot.send_message(message.chat.id,
                             '🔴 Period must be an integer value greater than zero',
                             reply_markup=single_cancel_button_markup())
            bot.register_next_step_handler(message, another_value_selected_handler)


def calendar_handler(message: object) -> None:
    '''
    Handler for calendar.
    This handler responds and validates to clicks from `calendar_markup`.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    elif message.text == button_titles.PREVIOUS:
        calendar_markup = tcalendar.calendar_previous_month(message)
        bot.send_message(message.chat.id, '⚪️ Please, choose a date', reply_markup=calendar_markup)
        bot.register_next_step_handler(message, calendar_handler)
    elif message.text == button_titles.NEXT:
        calendar_markup = tcalendar.calendar_next_month(message)
        bot.send_message(message.chat.id, '⚪️ Please, choose a date', reply_markup=calendar_markup)
        bot.register_next_step_handler(message, calendar_handler)
    elif tcalendar.date_validation(message.text):
        saved_date = tcalendar.current_shown_dates.get(message.chat.id)
        day = int(message.text)
        date = datetime(int(saved_date[0]), int(saved_date[1]), int(day), 0, 0, 0)
        if (date - lhelper.start_date).days >= 0:
            lhelper.period = int((date - lhelper.start_date).days) + 1
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        else:
            bot.send_message(message.chat.id, '🔴 Date must be greater than current')
            bot.register_next_step_handler(message, calendar_handler)
    else:
        bot.register_next_step_handler(message, calendar_handler)


def is_repeated_handler(message: object) -> None:
    '''
    Handler for choosing `is_repeated` value.
    This handler responds to clicks from `is_repeated_markup()`.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    elif message.text == button_titles.YES:
        lhelper.is_repeated = True
        set_limit_summary(message)
        bot.register_next_step_handler(message, set_limit_summary_handler)
    elif message.text == button_titles.NO:
        lhelper.is_repeated = False
        set_limit_summary(message)
        bot.register_next_step_handler(message, set_limit_summary_handler)
    else:
        bot.send_message(message.chat.id, '🔴 Please select one of the menu items')
        bot.register_next_step_handler(message, is_repeated_handler)


def set_limit_summary_handler(message):
    '''
    Handler for `set_limit_summary`.
    This handler responds to clicks from markup and any text input.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    elif message.text == button_titles.ACCEPT:
        bot.send_message(message.chat.id, '🔵 Limit created', reply_markup=ReplyKeyboardRemove())
        lhelper.insert_limit()
    else:
        bot.send_message(message.chat.id, '🔴 Please select one of the menu items')
        bot.register_next_step_handler(message, set_limit_summary_handler)


# Handlers for /clear_limit flow
@bot.message_handler(commands=['clear_limit'])
def clear_limit(message: object) -> None:
    '''
    Handler for "/clear_limit" command.

    :param object message: message object.
    :rtype: None.
    '''
    limit = lhelper.get_limit_record()
    if not limit:
        bot.send_message(message.chat.id, '🔴 There is no limits yet. Use /set_limit to create limit.')
    else:
        bot.send_message(message.chat.id, '⚪️ Please, choose a category', reply_markup=get_limit_markup(limit))
        bot.register_next_step_handler(message, clear_category_handler)


def clear_category_handler(message: object) -> None:
    '''
    Handler for choosing `category_name`.
    This handler responds to clicks from `set_category_markup()` and determines the further
    flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    existing_categories = lhelper.get_categories()
    if message.text == button_titles.CANCEL:
        cancel(message)
    elif message.text in existing_categories:
        lhelper.category_name = message.text
        bot.send_message(message.chat.id,
                         '🔵 You selected category: ' + message.text +
                         '⚪️ Do you want to delete the limit?',
                         reply_markup=accept_markup())
        bot.register_next_step_handler(message, clear_limit_summary_handler)
    else:
        bot.send_message(message.chat.id, '🔴 Please select one of the menu items')
        bot.register_next_step_handler(message, clear_category_handler)


def clear_limit_summary_handler(message):
    '''
    Handler for `set_limit_summary`.
    This handler responds to clicks from markup and any text input.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == button_titles.CANCEL:
        cancel(message)
    elif message.text == button_titles.ACCEPT:
        bot.send_message(message.chat.id, '🔵 Limit removed', reply_markup=ReplyKeyboardRemove())
        lhelper.clear_limit()
    else:
        bot.send_message(message.chat.id, '🔴 Please select one of the menu items')
        bot.register_next_step_handler(message, clear_limit_summary_handler)


@bot.message_handler(commands=['get_limit'])
def get_limit(message: object) -> None:
    limit = lhelper.get_limit_record()
    if not limit:
        bot.send_message(message.chat.id, '🔴 There is no limits yet. Use /set_limit to create limit.')
    else:
        bot.send_message(message.chat.id, '⚪️ Please, choose a category', reply_markup=get_limit_markup(limit))
        bot.register_next_step_handler(message, get_limit_handler)


def get_limit_handler(message: object) -> None:
    limit = lhelper.get_limit_record()
    if message.text == button_titles.CANCEL:
        cancel(message)
    else:
        index = 0
        for item in limit:
            if message.text in item:
                index = item[message.text]
        msg = (
            '🔵Limit for category "{title}"\n' +
            'Limit value: "{limit}"\n' +
            'Limitation period: "{period}"\n' +
            'Budget mode: "{is_repeated}"\n' +
            'Start from: "{start_date}"'
        ).format(**limit[index])

        bot.send_message(message.chat.id, msg)
