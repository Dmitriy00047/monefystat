from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from database.models import Transaction, Category
from config import db


def insert_transactions(transactions) -> None:
    '''
        Inserts prepared data to database.
        All data must correspond with Transaction model.

        :param transactions: list of lists of converted data from csv file.
        :param engine: connected database engine.
    '''
    engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(**db))

    connection = engine.connect()
    for transaction in transactions:
        category = transaction[2].strip().lower()
        category_id = insert_category_2_bd(category, connection)
        insert_transaction = insert(Transaction).values(
            transaction_date=transaction[0],
            account=transaction[1],
            category=category_id,
            amount=abs(transaction[3]),
            currency=transaction[4],
            converted_amount=abs(transaction[5]),
            converted_currency=transaction[6],
            description=transaction[7],
            is_debet=(transaction[3] > 0)
        )
        on_update_transaction = insert_transaction.on_conflict_do_update(
            constraint='tr_constraint',
            set_=dict(
                category=category_id,
                currency=transaction[4],
                converted_amount=abs(transaction[5]),
                converted_currency=transaction[6],
                is_debet=(transaction[3] > 0)
            )
        )
        connection.execute(on_update_transaction)
    connection.close()


def insert_category_2_bd(category: str, connection: object) -> int:
    '''
        Check that category exists in the db table.
        If not - insert category to bd.

        :param category: the name of the category.
        :param connection: connection string to bd.
    '''
    insert_category = insert(Category).values(
        title=category
    )
    do_nothing_category = insert_category.on_conflict_do_nothing(
        index_elements=['title']
    )
    res = connection.execute(do_nothing_category)
    if res.inserted_primary_key:
        return res.inserted_primary_key[0]
    else:
        return get_category_id(category, connection)


def get_category_id(category: str, connection: object) -> int:
    '''
        Get id from db table by the title.

        :param category: the name of the category.
        :param connection: connection string to bd.
    '''
    res = select([Category.id]).where(Category.title == category)
    out = connection.execute(res)
    return out.fetchone()[0]
