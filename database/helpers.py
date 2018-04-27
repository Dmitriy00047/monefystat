import psycopg2
from aiopg.sa import create_engine
from config import db
from sqlalchemy import select
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.dialects.postgresql import insert
from database.models import Transaction, Category

dsn_def = 'postgresql://{user}:{password}@{host}:{port}'.format(**db)
dsn = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(**db)


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
            await connection.execute("create database monefystat")
            await _prepare_tables()


async def drop_db():
    """Asynchronous function for dropping database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("drop database monefystat")


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
    engine = create_sync_engine(dsn)
    conn = engine.connect()
    if category_name:
        s = select([Category]).where(Category.title == category_name)
    else:
        s = select([Category])

    result = conn.execute(s)

    return _convert_resultproxy_to_dictionary(result)


async def upsert_limit(category_name, **kwargs) -> None:
    """
    Asynchronous function for inserting and updating data.

    Warning: **kwargs must accept only the specified parameters.

    :param str category_name: name of selecting category.
    :param float limit: limit of categody.
    :param datetime start_date: start day of limit.
    :param int period: number of days for limit.
    :param bool is_repeated: checking limit should be repeated for the same period.
    :rtype: None
    """
    engine = create_sync_engine(dsn)
    conn = engine.connect()
    ins = insert(Category).values(dict(title=category_name, **kwargs))

    do_update_category = ins.on_conflict_do_update(index_elements=['title'], set_=kwargs)
    conn.execute(do_update_category)
    conn.close()


async def delete_limit(category_name: str) -> None:
    """
    Asynchronous function function for clearing limit.

    :param str category_name: name of category to clean.
    :rtype: None.
    """
    category = Category.__table__
    delete = category.update().where(Category.title == category_name).values(limit=None,
                                                                             start_date=None,
                                                                             period=None,
                                                                             is_repeated=None)
    engine = create_sync_engine(dsn)
    conn = engine.connect()
    conn.execute(delete)
    conn.close()
