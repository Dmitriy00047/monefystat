from datetime import datetime

import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram_bot.telegram_calendar import TelegramCalendar
from telegram_bot.limiter_helper import LimiterHelper
from config import telegram


bot = telebot.TeleBot(telegram['token'], threaded=False)
lhelper = LimiterHelper()
tcalendar = TelegramCalendar()


# Markups for /set_limit flow
def single_cancel_button_markup() -> object:
    '''
    Function returns markup with only one button '❌ Отмена'.

    :rtype: ReplyKeyboardMarkup.
    '''
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('❌ Отмена')
    return keyboard


def set_category_markup() -> object:
    '''
    Function returns markup with all existing categories and '🆕 Ввести категорию' and '❌ Отмена' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    existing_categories = lhelper.get_categories()
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for entry in existing_categories:
        keyboard.row(entry)
    keyboard.row('🆕 Ввести категорию')
    keyboard.row('❌ Отмена')
    return keyboard


def set_period_markup() -> object:
    '''
    Function returns markup with predefined periods and 'Другое значение', 'Выбрать дату', and '❌ Отмена' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('День', 'Неделя')
    keyboard.row('Месяц', 'Год')
    keyboard.row('Другое значение', 'Выбрать дату')
    keyboard.row('❌ Отмена')
    return keyboard


def is_repeated_markup() -> object:
    '''
    Function returns markup with '✅ Да', '❎ Нет', and '❌ Отмена' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('✅ Да', '❎ Нет')
    keyboard.row('❌ Отмена')
    return keyboard


def set_limit_summary_markup():
    '''
    Function returns markup with '✅ Подтвердить' and '❌ Отмена' buttons.

    :rtype: ReplyKeyboardMarkup.
    '''
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('✅ Подтвердить')
    keyboard.row('❌ Отмена')
    return keyboard


# Helpers funcs for /set_limit flow
def cancel(message: object) -> None:
    '''
    Message response function on 'cancel_message'.

    :param object message: message object.
    :rtype: None.
    '''
    clr_keyboard = ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, '🔵 Отменено', reply_markup=clr_keyboard)


def set_limit_summary(message: object) -> None:
    '''
    Function sends message of summary of creating limit.

    :param object message: message object.
    :rtype: None.
    '''
    if lhelper.is_repeated:
        budget = 'Включен'
    else:
        budget = 'Выключен'
    text_off_message = '🔵 Вы хотите создать лимит\n'\
                       'Категория: {category_name}\n'\
                       'Лимит: {limit}\n'\
                       'Период: {period}\n'\
                       'Режим бютжета: {budget}\n'\
                       'Начало: {start_date}\n'.format(category_name=lhelper.category_name,
                                                       limit=lhelper.limit,
                                                       period=lhelper.period,
                                                       start_date=lhelper.start_date.date(),
                                                       budget=budget)
    bot.send_message(message.chat.id, text_off_message, reply_markup=set_limit_summary_markup())


def is_repeated_question(message: object) -> None:
    '''
    Function sends question message of repeating limit (budget mode).

    :param object message: message object.
    :rtype: None.
    '''
    bot.send_message(message.chat.id,
                     '🔵 Вы установили период (дней): ' + str(lhelper.period) + '\n' +
                     '⚪️ Включить режим бюджета (повторение периода)?',
                     reply_markup=is_repeated_markup())


# Handlers for /set_limit flow
@bot.message_handler(commands=['set_limit'])
def set_limit(message: object) -> None:
    '''
    Handler for "/set_limit" command.

    :param object message: message object.
    :rtype: None.
    '''
    bot.send_message(message.chat.id, '⚪️ Выберите категорию', reply_markup=set_category_markup())
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
    if message.text == '❌ Отмена':
        cancel(message)
    elif message.text == '🆕 Ввести категорию':
        bot.send_message(message.chat.id, '⚪️ Введите название категории', reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, category_entered_value_handler)
    elif message.text in existing_categories:
        lhelper.category_name = message.text
        bot.send_message(message.chat.id,
                         '🔵 Вы выбрали категорию : ' + message.text + '\n' +
                         '⚪️ Введите значение лимита (UAH)',
                         reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, set_limit_value_handler)
    else:
        bot.send_message(message.chat.id, '🔴 Пожалуйста выберите один из пунктов меню')
        bot.register_next_step_handler(message, set_category_handler)


def category_entered_value_handler(message: object) -> None:
    '''
    Handler for manual input of `category_name`.
    This handler responds to clicks from `single_cancel_button_markup()` and manual inputting of any text.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == '❌ Отмена':
        cancel(message)
    else:
        lhelper.category_name = message.text
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row('✅ Подтвердить')
        keyboard.row('❎ Изменить')
        keyboard.row('❌ Отмена')
        bot.send_message(message.chat.id,
                         '⚪️ Вы создаете лимит для категории: ' + message.text,
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, category_accept_handler)


def category_accept_handler(message: object) -> None:
    '''
    Handler for manual input of `category_name`.
    This handler responds to clicks from `single_cancel_button_markup()` and manual inputting of any text.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == '❌ Отмена':
        cancel(message)
    elif message.text == '❎ Изменить':
        bot.send_message(message.chat.id, '⚪️ Введите название категории', reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, category_entered_value_handler)
    elif message.text == '✅ Подтвердить':
        bot.send_message(message.chat.id,
                         '🔵 Вы выбрали категорию : ' + lhelper.category_name + '\n' +
                         '⚪️ Введите значение лимита (UAH)',
                         reply_markup=single_cancel_button_markup())
        bot.register_next_step_handler(message, set_limit_value_handler)
    else:
        bot.send_message(message.chat.id, '🔴 Пожалуйста выберите один из пунктов меню')
        bot.register_next_step_handler(message, category_accept_handler)


def set_limit_value_handler(message: object) -> None:
    '''
    Handler for manual input of `limit`.
    This handler responds and validates to manual inputting of limit.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == '❌ Отмена':
        cancel(message)
    else:
        if lhelper.validate_limit(message.text):
            lhelper.start_date = datetime.utcnow()
            lhelper.limit = float(message.text)
            bot.send_message(message.chat.id,
                             '🔵 Вы ввели лимит: ' + message.text + '\n' +
                             '⚪️ Выберите период',
                             reply_markup=set_period_markup())
            bot.register_next_step_handler(message, set_period_handler)
        else:
            bot.send_message(message.chat.id,
                             '🔴 Значение лимита должно быть числовым значением больше нуля',
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
    if message.text == '❌ Отмена':
        cancel(message)
    else:
        if message.text == 'День':
            lhelper.period = 1
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == 'Неделя':
            lhelper.period = 7
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == 'Месяц':
            lhelper.period = 30
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == 'Год':
            lhelper.period = 365
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        elif message.text == 'Другое значение':
            bot.send_message(message.chat.id,
                             '⚪️ Введите количество дней на которое вы желаете установить лимит:',
                             reply_markup=single_cancel_button_markup())
            bot.register_next_step_handler(message, another_value_selected_handler)
        elif message.text == 'Выбрать дату':
            calendar_markup = tcalendar.calendar_today(message)
            bot.send_message(message.chat.id, '⚪️ Пожалуйста выберите дату', reply_markup=calendar_markup)
            bot.register_next_step_handler(message, calendar_handler)
        else:
            bot.send_message(message.chat.id, '🔴 Пожалуйста выберите один из пунктов меню')
            bot.register_next_step_handler(message, set_period_handler)


def another_value_selected_handler(message: object) -> None:
    '''
    Handler for manual input of `period`.
    This handler responds to clicks from `single_cancel_button_markup()` and validates manual inputting of period.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == '❌ Отмена':
        cancel(message)
    else:
        if lhelper.validate_period(message.text):
            lhelper.period = int(message.text)
            is_repeated_question(message)
            bot.register_next_step_handler(message, is_repeated_handler)
        else:
            keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
            keyboard.row('❌ Отмена')
            bot.send_message(message.chat.id,
                             '🔴 Период должен представлять собой целочисленное значение больше нуля',
                             reply_markup=keyboard)
            bot.register_next_step_handler(message, another_value_selected_handler)


def calendar_handler(message: object) -> None:
    '''
    Handler for calendar.
    This handler responds and validates to clicks from `calendar_markup`.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == '❌ Отмена':
        cancel(message)
    elif message.text == '⬅️':
        calendar_markup = tcalendar.calendar_previous_month(message)
        bot.send_message(message.chat.id, '⚪️ Пожалуйста выберите дату', reply_markup=calendar_markup)
        bot.register_next_step_handler(message, calendar_handler)
    elif message.text == '➡️':
        calendar_markup = tcalendar.calendar_next_month(message)
        bot.send_message(message.chat.id, '⚪️ Пожалуйста выберите дату', reply_markup=calendar_markup)
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
            bot.send_message(message.chat.id, '🔴 Дата должна быть больше текущей')
            bot.register_next_step_handler(message, calendar_handler)


def is_repeated_handler(message: object) -> None:
    '''
    Handler for choosing `is_repeated` value.
    This handler responds to clicks from `is_repeated_markup()`.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == '❌ Отмена':
        cancel(message)
    elif message.text == '✅ Да':
        lhelper.is_repeated = True
        set_limit_summary(message)
        bot.register_next_step_handler(message, set_limit_summary_handler)
    elif message.text == '❎ Нет':
        lhelper.is_repeated = False
        set_limit_summary(message)
        bot.register_next_step_handler(message, set_limit_summary_handler)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста выберите один из пунктов меню')
        bot.register_next_step_handler(message, is_repeated_handler)


def set_limit_summary_handler(message):
    '''
    Handler for `set_limit_summary`.
    This handler responds to clicks from markup and any text input.
    Determines the further flow of the setting of limit.

    :param object message: message object.
    :rtype: None.
    '''
    if message.text == '❌ Отмена':
        cancel(message)
    elif message.text == '✅ Подтвердить':
        bot.send_message(message.chat.id, '🔵 Лимит создан', reply_markup=ReplyKeyboardRemove())
        lhelper.insert_limit()
    else:
        bot.send_message(message.chat.id, '🔴 Пожалуйста выберите один из пунктов меню')
        bot.register_next_step_handler(message, set_limit_summary_handler)
