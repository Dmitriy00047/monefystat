import asyncio
from datetime import datetime

from database.helpers import \
    get_limit, \
    upsert_limit, \
    delete_limit, \
    get_data_period


class LimiterHelper(object):
    '''
    This is LimiterHelper class. Use it for accumulating data for
    "/set_limit", "/get_limit", "/delete_limit" commands in telegram bot.
    Methods:
        validate_limit
        validate_period
    '''
    def __init__(self):
        self.__category_name = None
        self.__limit = None
        self.__period = None
        self.__start_date = datetime.utcnow()
        self.__is_repeated = False
        self.__start_period = None
        self.__end_period = datetime.utcnow()
        self.handler = None
        self.__chat_id = None

    @property
    def category_name(self):
        return self.__category_name

    @category_name.setter
    def category_name(self, value):
        if isinstance(value, str):
            self.__category_name = value
        else:
            raise TypeError()

    @property
    def limit(self):
        return self.__limit

    @limit.setter
    def limit(self, value):
        if isinstance(value, float):
            self.__limit = value
        else:
            raise TypeError()

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, value):
        if isinstance(value, int):
            self.__period = value
        else:
            raise TypeError()

    @property
    def start_date(self):
        return self.__start_date

    @start_date.setter
    def start_date(self, value):
        self.__start_date = value

    @property
    def start_period(self):
        return self.__start_period

    @start_period.setter
    def start_period(self, value):
        if isinstance(value, datetime):
            self.__start_period = value
        else:
            raise TypeError()

    @property
    def end_period(self):
        return self.__end_period

    @end_period.setter
    def end_period(self, value):
        if isinstance(value, datetime):
            self.__end_period = value
        else:
            raise TypeError()

    @property
    def is_repeated(self):
        return self.__is_repeated

    @is_repeated.setter
    def is_repeated(self, value):
        if isinstance(value, bool):
            self.__is_repeated = value
        else:
            raise TypeError()

    @property
    def chat_id(self):
        return self.__chat_id

    @chat_id.setter
    def chat_id(self, value):
        try:
            self.__chat_id = int(value)
        except Exception:
            raise TypeError()

    def validate_limit(self, value: type) -> bool:
        '''
        Function validates limit value returns True if validation successful, False if not.

        :param type value: value for validation.
        :rtype: bool.
        '''
        try:
            if float(value) > 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def validate_period(self, value: type) -> bool:
        '''
        Function validates period value returns True if validation successful, False if not.

        :param type value: value for validation.
        :rtype: bool.
        '''
        try:
            if int(value) > 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def get_categories(self) -> list:
        result = []
        loop = asyncio.get_event_loop()
        limits = loop.run_until_complete(get_limit())
        for lim in limits:
            result.append(lim['title'])
        return result

    def insert_limit(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(upsert_limit(self.__category_name,
                                             limit=self.__limit,
                                             period=self.__period,
                                             start_date=self.__start_date,
                                             is_repeated=self.__is_repeated))

    def get_period_for_category(self) -> list:
        result = []
        start_date = None
        loop = asyncio.get_event_loop()
        end_date = str(self.__end_period.strftime('%d-%m-%Y'))
        if self.__start_period:
            start_date = str(self.__start_period.strftime('%d-%m-%Y'))
        transactions = loop.run_until_complete(get_data_period(self.__category_name,
                                                               period=self.__period,
                                                               start_date=start_date,
                                                               end_date=end_date
                                                               ))
        for transaction in transactions:
            if transaction:
                msg = 'date: {0}, account: {1}, amount: {2}, currency: {3}'.format(
                    transaction['transaction_date'],
                    transaction['account'],
                    transaction['amount'],
                    transaction['currency']
                )
                result.append(msg)
        return result

    def clear_limit(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(delete_limit(self.__category_name))

    def get_limit_record(self) -> list:
        result = []
        loop = asyncio.get_event_loop()
        limits = loop.run_until_complete(get_limit())
        for lim in limits:
            if lim['limit']:
                result.append(lim)
        return result

    def check_pass_limit(self) -> list:
        result = []
        limits = self.get_limit_record()
        for limit in limits:
            self._choose_limit(limit)
            current_amount = self._get_current_amount_for_limit(limit['title'])
            current_limit = limit['limit']
            if (datetime.utcnow().date() - self.start_date).days < self.period:
                if current_amount > 0.7 * current_limit and current_amount < current_limit:
                    result.append('You are approaching the limit on category: {category_name}.\n'
                                  'Your limit value: {limit_value}.\n'
                                  'Your current amount: {current_amount}.'.format(category_name=limit['title'],
                                                                                  limit_value=current_limit,
                                                                                  current_amount=current_amount))
                elif current_amount > current_limit:
                    result.append('You exceeded the limit on category: {category_name}.\n'
                                  'Your limit value: {limit_value}.\n'
                                  'Your current amount: {current_amount}.'.format(category_name=limit['title'],
                                                                                  limit_value=current_limit,
                                                                                  current_amount=current_amount))
        return result

    def _choose_limit(self, limit: dict) -> None:
        self.category_name = limit['title']
        self.limit = limit['limit']
        self.period = limit['period']
        self.start_date = limit['start_date']

    def _get_current_amount_for_limit(self, category_name) -> float:
        result = 0.0
        loop = asyncio.get_event_loop()
        transactions = loop.run_until_complete(get_data_period(self.__category_name,
                                                               period=None,
                                                               start_date=self.start_date,
                                                               end_date=datetime.utcnow()))
        for transaction in transactions:
            if transaction:
                result += float(transaction['amount'])

        return result
