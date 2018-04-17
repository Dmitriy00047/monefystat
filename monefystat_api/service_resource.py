from aiopg.sa import create_engine
from config import db_config
import asyncio

dsn = 'user={user} password={password} host={host} port={port}'.format(**db_config)


async def _create_default_engine():
    """Asynchronous function for creating engine."""
    default_engine = await create_engine(dsn)
    return default_engine


async def _create_db():
    """Asynchronous function for creating database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("create database {}".format(db_config['db_name']))


async def _drop_db():
    """Asynchronous function for dropping database."""
    default_engine = await _create_default_engine()
    async with default_engine:
        async with default_engine.acquire() as connection:
            await connection.execute("drop database {}".format(db_config['db_name']))


def create_db_endpoint():
    """Function for asynchronous creating database endpoint."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_create_db())
    loop.close()


def drop_db_endpoint():
    """Function for asynchronous dropping database endpoint."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_drop_db())
    loop.close()
