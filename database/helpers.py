import psycopg2
from aiopg.sa import create_engine
from config import db_config
from sqlalchemy.schema import CreateTable, DropTable
from database.models import Transaction

dsn_def = 'user={user} password={password} host={host} port={port}'.format(**db_config)
dsn = 'user={user} dbname={dbname} host={host} password={password}'.format(**db_config)


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
            await connection.execute("create database {}".format(db_config['dbname']))
            await _prepare_tables()


async def drop_db():
    """Asynchronous function for dropping database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("drop database {}".format(db_config['dbname']))


async def _prepare_tables():
    """Asynchronous function for creating tables in database."""
    tables = [Transaction.__table__]
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
    async with engine:
        async with engine.acquire() as connection:
            query = 'select * from Transaction'
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
