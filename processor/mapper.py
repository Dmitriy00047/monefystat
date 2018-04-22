from database.models import Transaction, Category
from sqlalchemy.orm import Session


def insert_transactions(transactions, engine) -> None:
    '''
        Inserts prepared data to database.
        All data must correspond with Transaction model.

        :param transactions: list of lists of converted data from csv file.
        :param engine: connected database engine.
    '''
    session = Session(bind=engine)
    session.add_all([
        Transaction(
            transaction_date=transaction[0],
            account=transaction[1],
            category=add_category_2_bd(transaction[2].strip().lower(), engine),
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


def add_category_2_bd(category, engine: str) -> int:
    '''
        Inserts prepared data to the db table.
        All data must correspond with Category model.

        :param category: the name of the category.
        :param engine: connected database engine.
    '''
    session = Session(bind=engine)
    model = Category()
    if check_category_exist(category, session):
        model.title = category
        session.add(model)
        session.commit()
        session.flush()
        return model.id
    else:
        return get_category_id(category, session)


def check_category_exist(category: str, session: object) -> bool:
    '''
        Check that category exists in the db table.

        :param category: the name of the category.
        :param session: Session object.
    '''
    res = session.query(Category).filter(Category.title == category).all()
    if not res:
        return True
    return False


def get_category_id(category: str, session: object) -> int:
    '''
        Get id from db table by the title.

        :param category: the name of the category.
        :param session: Session object.
    '''
    res = session.query(Category).filter(Category.title == category).first()
    return res.id
