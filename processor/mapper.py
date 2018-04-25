from database.models import Transaction
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import db


def insert_transactions(transactions) -> None:
    '''
        Inserts prepared data to database.
        All data must correspond with Transaction model.

        :param transactions: list of lists of converted data from csv file.
        :param engine: connected database engine.
    '''
    engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(**db))
    session = Session(bind=engine)
    session.add_all([
        Transaction(
            transaction_date=transaction[0],
            account=transaction[1],
            category=transaction[2],
            amount=abs(transaction[3]),
            currency=transaction[4],
            converted_amount=abs(transaction[5]),
            converted_currency=transaction[6],
            description=transaction[7],
            is_debet=(transaction[3] > 0)
        )
        for transaction in transactions
    ])
    session.commit()
    engine.dispose()
