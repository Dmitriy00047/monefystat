import psycopg2
from datetime import datetime, timedelta
from aiopg.sa import create_engine
from config import db
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy import select, and_
from database.models import Transaction
from database.models import Category
from sqlalchemy import create_engine as alchemy_create_engine

# dsn_def = 'user={user} password={password} host={host} port={port}'.format(**db)
# dsn = 'user={user} dbname={dbname} host={host} password={password}'.format(**db)

dsn_def = 'postgresql://postgres:password@localhost:5432'
dsn = 'postgresql://postgres:password@localhost:5432/monefystat'


async def _create_default_engine():
    """Asynchronous function for creating default engine."""
    default_engine = await create_engine(dsn_def)
    return default_engine


async def _create_engine():
    """Asynchronous function for creating engine."""
    engine = await create_engine(dsn)
    return engine


async def create_db():
    """Asynchronous function for creating database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("create database {}".format(db['dbname']))
            await _prepare_tables()


async def drop_db():
    """Asynchronous function for dropping database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("drop database {}".format(db['dbname']))


async def _prepare_tables():
    """Asynchronous function for creating tables in database."""
    tables = [Category.__table__, Transaction.__table__]
    engine = await _create_engine()
    async with engine:
        async with engine.acquire() as connection:
            await _drop_tables(engine, tables)
            for table in tables:
                create_query = CreateTable(table)
                await connection.execute(create_query)


async def _drop_tables(engine, tables):
    """
    Asynchronous function for dropping tables in database.

    :param Engine engine: engine of database
    :param list tables: list of tables to dropping
    """
    async with engine.acquire() as connection:
        for table in reversed(tables):
            drop_query = DropTable(table)
            try:
                await connection.execute(drop_query)
            except psycopg2.ProgrammingError:
                pass


async def get_all_data():
    """
    Asynchronous function for getting all data from database.
    :return list: list of dictionaries with all data
    """
    engine = await _create_engine()
    async with engine.acquire() as connection:
        query = 'select * from transaction'
        result = await connection.execute(query)
        return _convert_resultproxy_to_dictionary(result)


def _convert_resultproxy_to_dictionary(result_proxy):
    """
    Convert ResultProxy object to list of dictionaries.

    :param ResultProxy result_proxy: ResultProxy object to convert
    :return list: list of dictionaries
    """
    dict_result = []
    for row in result_proxy:
        dict_result.append(dict(row))
    return dict_result


async def get_data_define_period(category_name, period):
    """
    Function for getting all data for specified category and period(days) from database.
    :param str category_name: bytearray with name of category
    :param str period: some digit which represent some period in past from current date
    """
    engine = alchemy_create_engine(dsn)
    conn = engine.connect()
    cur_date = str(datetime.date(datetime.now()))
    period_date = str(datetime.date(datetime.now()) - timedelta(int(period)))
    category_name = list(map(lambda x: x.replace(" ", ""), category_name[:7]))
    category_name = list(map(lambda x: x.replace("\xa0", ""), category_name[:7]))
    category_name = "".join(category_name)
    id_query = select([Category.id]).where(Category.title == category_name)
    result = conn.execute(id_query)
    try:
        id = _convert_resultproxy_to_dictionary(result)[0]['id']
    except IndexError:
        return 'There is no such category'
    data_query = select([Transaction]).where(
        and_(
            Transaction.category == id,
            (Transaction.transaction_date.between(period_date, cur_date))
            )
        )
    result = conn.execute(data_query)
    return _convert_resultproxy_to_dictionary(result)


async def get_data_custom_period(category_name, start_date, end_date):
    try:
        s_date = datetime.strptime(start_date, "%Y-%m-%d")
        e_date = datetime.strptime(end_date, "%Y-%m-%d")
        if s_date > e_date:
            start_date, end_date = end_date, start_date
    except ValueError:
        return "Invalid dates"

    engine = alchemy_create_engine(dsn)
    conn = engine.connect()
    category_name = list(map(lambda x: x.replace(" ", ""), category_name[:7]))
    category_name = list(map(lambda x: x.replace("\xa0", ""), category_name[:7]))
    category_name = "".join(category_name)
    id_query = select([Category.id]).where(Category.title == category_name)
    result = conn.execute(id_query)
    try:
        id = _convert_resultproxy_to_dictionary(result)[0]['id']
    except IndexError:
        return 'There is no such category'
    data_query = select([Transaction]).where(
        and_(
            Transaction.category == id,
            (Transaction.transaction_date.between(start_date, end_date))
            )
        )
    result = conn.execute(data_query)
    return _convert_resultproxy_to_dictionary(result)
