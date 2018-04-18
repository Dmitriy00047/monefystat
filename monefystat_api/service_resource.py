import asyncio
from database.helpers import create_db, drop_db, get_all_data


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


def get_all_data_endpoint():
    """
    Function for asynchronous getting all data from database endpoint.

    :return list: list of dictionaries with all data
    """
    loop = asyncio.get_event_loop()
    all_data = loop.run_until_complete(get_all_data())
    loop.close()
    return all_data
