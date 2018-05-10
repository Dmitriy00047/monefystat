import sys
import inspect
from typing import List, Dict
from collections import namedtuple
from datetime import datetime, timedelta

import psycopg2
from aiopg.sa import create_engine
from sqlalchemy import select, and_
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.dialects.postgresql import insert

from database import models
from database.models import Transaction, Category
from config import db

dsn_def = 'user={user} password={password} host={host} port={port}'.format(**db)
dsn = 'user={user} dbname={dbname} host={host} password={password}'.format(**db)


async def _create_default_engine():
    '''Asynchronous function for creating default engine.'''
    default_engine = await create_engine(dsn_def)
    return default_engine


async def _create_engine():
    '''Asynchronous function for creating engine.'''
    engine = await create_engine(dsn)
    return engine


async def create_db() -> None:
    '''Asynchronous function for creating database.'''
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute('create database {}'.format(db['dbname']))
            await _prepare_tables()


async def drop_db() -> None:
    '''Asynchronous function for dropping database.'''
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute('drop database {}'.format(db['dbname']))


async def _get_model_classes() -> list:
    ''' Asynchronous function for getting model classes. '''
    Clsmember = namedtuple('Clsmember', ['cls_name', 'cls_def'])
    clsmembers = [Clsmember(member[0], member[1]) for member in inspect.getmembers(sys.modules[models.__name__],
                                                                                   inspect.isclass)]

    accumulator = []
    for el in clsmembers:
        if el.cls_name != models.Base.__name__ and issubclass(el.cls_def, models.Base):
            accumulator.append(el)
    return accumulator


async def _get_tables() -> list:
    ''' Asynchronous function for getting tables. '''
    model_classes = await _get_model_classes()
    result = []
    for model in model_classes:
        result.append(model.cls_def.__table__)
    return result


async def _prepare_tables() -> None:
    '''Asynchronous function for creating tables in database.'''
    tables = await _get_tables()
    engine = await _create_engine()
    async with engine:
        async with engine.acquire() as connection:
            await _drop_tables(engine, tables)
            for table in tables:
                create_query = CreateTable(table)
                await connection.execute(create_query)


async def _drop_tables(engine, tables):
    '''
    Asynchronous function for dropping tables in database.

    :param Engine engine: engine of database
    :param list tables: list of tables to dropping
    '''
    async with engine.acquire() as connection:
        for table in reversed(tables):
            drop_query = DropTable(table)
            try:
                await connection.execute(drop_query)
            except psycopg2.ProgrammingError:
                pass


async def get_all_data() -> list:
    '''
    Asynchronous function for getting all data from database.
    :return list: list of dictionaries with all data
    '''
    engine = await _create_engine()
    async with engine.acquire() as connection:
        query = 'select * from transaction'
        result = await connection.execute(query)
        return _convert_resultproxy_to_dictionary(result)


def _convert_resultproxy_to_dictionary(result_proxy):
    '''
    Convert ResultProxy object to list of dictionaries.

    :param ResultProxy result_proxy: ResultProxy object to convert
    :return list: list of dictionaries
    '''
    dict_result = []
    for row in result_proxy:
        dict_result.append(dict(row))
    return dict_result


async def get_data_period(category_name: str, period=None, start_date=None, end_date=None) -> list:
    '''
    Asynchronous function for getting all data for specified category and period(days) from database.
    :param str category_name: bytearray with name of category
    :param str period: some digit which represent some period in past from current date
    :param str start_date: start date of the period
    :param str end_date: end date of the period
    '''
    start_date, end_date = _date_validator(period=period, start_date=start_date, end_date=end_date)
    category_name = _category_name_decoder(category_name)
    engine = await _create_engine()
    async with engine.acquire() as connection:
        id_query = select([Category.id]).where(Category.title == category_name)
        data_query = select([Transaction]).where(
            and_(
                Transaction.category == id_query,
                (Transaction.transaction_date.between(start_date, end_date))
                )
            )
        result = await connection.execute(data_query)
    return _convert_resultproxy_to_dictionary(result)


def _category_name_decoder(category_name: str) -> str:
    '''
    Function for decoding category name from bytearray to string
    :param str category_name: bytearray with name of category
    '''
    category_name = list(map(lambda x: x.replace(' ', ''), category_name))
    category_name = list(map(lambda x: x.replace('\xa0', ''), category_name))
    category_name = ''.join(category_name)
    return category_name.strip().lower()


def _date_validator(period=None, start_date=None, end_date=None) -> tuple:
    ''' Function for syncing to database format '''
    if period:
        end_date = datetime.date(datetime.now())
        start_date = datetime.date(datetime.now()) - timedelta(int(period))
    else:
        try:
            start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            if start_date > end_date:
                start_date, end_date = end_date, start_date
        except ValueError:
            return 'Invalid dates'
    return start_date, end_date


async def get_limit(category_name=None) -> List[Dict]:
    '''
    Asynchronous function for getting data from category table.

    :param str category_name: name of selecting category.
    :return list: list of dictionaries like this:
        [
            {
                'id': int,
                'timestamp': datetime,
                'title': category_name,
                'limit': float,
                'start_date': datetime,
                'period': int,
                'is_repeated': bool
            }
        ]
    '''
    engine = await _create_engine()
    async with engine:
        async with engine.acquire() as connection:
            if category_name:
                s = select([Category]).where(Category.title == category_name)
            else:
                s = select([Category])

            result = await connection.execute(s)
            return _convert_resultproxy_to_dictionary(result)


async def upsert_limit(category_name, **kwargs) -> None:
    '''
    Asynchronous function for inserting and updating data.

    Warning: **kwargs must accept only the specified parameters.

    :param str category_name: name of selecting category.
    :param float limit: limit of category.
    :param datetime start_date: start day of limit.
    :param int period: number of days for limit.
    :param bool is_repeated: checking limit should be repeated for the same period.
    :rtype: None
    '''
    engine = await _create_engine()
    async with engine:
        async with engine.acquire() as connection:
            ins = insert(Category).values(dict(title=category_name, **kwargs))
            do_update_category = ins.on_conflict_do_update(index_elements=['title'], set_=kwargs)
            await connection.execute(do_update_category)


async def delete_limit(category_name: str) -> None:
    '''
    Asynchronous function function for clearing limit.

    :param str category_name: name of category to clean.
    :rtype: None.
    '''
    category = Category.__table__
    engine = await _create_engine()
    async with engine:
        async with engine.acquire() as connection:
            delete = category.update().where(Category.title == category_name).values(limit=None,
                                                                                     start_date=None,
                                                                                     period=None,
                                                                                     is_repeated=None)
            await connection.execute(delete)
