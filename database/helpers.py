import psycopg2
from datetime import datetime
from aiopg.sa import create_engine
from config import db
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy import select
from database.models import Transaction
from database.models import Category
from sqlalchemy import create_engine as cren

# dsn_def = 'user={user} password={password} host={host} port={port}'.format(**db)
# dsn = 'user={user} dbname={dbname} host={host} password={password}'.format(**db)

dsn_def = 'postgresql://user:password@localhost:5432'
dsn = 'postgresql://user:password@localhost:5432/monefystat'


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


async def get_limit(category_name=None) -> list:
    """
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
    """
    engine = cren(dsn)
    conn = engine.connect()
    if category_name:
        s = select([Category]).where(Category.title == category_name)
    else:
        s = select([Category])

    result = conn.execute(s)
    return _convert_resultproxy_to_dictionary(result)


async def add_limit(title: str, limit: float, start_date: datetime, period: int, is_repeated: bool) -> None:
    args = {
        'title': title,
        'limit': limit,
        'start_date': start_date,
        'period': period,
        'is_repeated': is_repeated
    }
    category = Category.__table__
    ins = category.insert().values(args)
    engine = cren(dsn)
    conn = engine.connect()
    conn.execute(ins)


async def update_limit(category_name: str, **kwargs):
    category = Category.__table__
    upd = category.update().where(Category.title == category_name).values(kwargs)
    engine = cren(dsn)
    conn = engine.connect()
    conn.execute(upd)


async def delete_limit(category_name: str):
    category = Category.__table__
    delete = category.delete().where(Category.title == category_name)
    engine = cren(dsn)
    conn = engine.connect()
    conn.execute(delete)
