from aiopg.sa import create_engine
from config import db_config

dsn = 'user={user} password={password} host={host} port={port}'.format(**db_config)


async def _create_default_engine():
    """Asynchronous function for creating engine."""
    default_engine = await create_engine(dsn)
    return default_engine


async def create_db():
    """Asynchronous function for creating database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("create database {}".format(db_config['db_name']))


async def drop_db():
    """Asynchronous function for dropping database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("drop database {}".format(db_config['db_name']))
