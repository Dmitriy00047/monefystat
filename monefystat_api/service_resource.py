import asyncio
from database.helpers import create_db, drop_db


def create_db_endpoint():
    """Function for asynchronous creating database endpoint."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
    loop.close()


def drop_db_endpoint():
    """Function for asynchronous dropping database endpoint."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(drop_db())
    loop.close()
