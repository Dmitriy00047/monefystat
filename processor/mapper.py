from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import select
from database.models import Transaction, Category
from database.helpers import _create_engine


async def insert_transactions(transactions: list) -> None:
    '''
    Inserts prepared data to database.
    All data must correspond with Transaction model.

    :param transactions: list of lists of converted data from csv file.
    '''
    engine = await _create_engine()
    async with engine:
        async with engine.acquire() as connection:
            for transaction in transactions:
                category = transaction[2].strip().lower()
                category_id = await insert_select_category(category, connection)
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
                await connection.execute(on_update_transaction)


async def insert_select_category(category: str, connection: object) -> int:
    '''
    Check that category exists in the db table.
    If not - insert category to bd.

    :param category: the name of the category.
    :param connection: connection object.
    '''
    insert_category = insert(Category).values(title=category)
    do_nothing_category = insert_category.on_conflict_do_nothing(index_elements=['title'])
    res = await connection.execute(do_nothing_category)
    row = await res.first()
    if not row:
        return await get_category_id(category, connection)
    return row['id']


async def get_category_id(category: str, connection: object) -> int:
    '''
    Get id from db table by the title.

    :param category: the name of the category.
    :param connection: connection object.
    '''
    res = select([Category.id]).where(Category.title == category)
    out = await connection.execute(res)
    row = await out.first()
    return row['id']
