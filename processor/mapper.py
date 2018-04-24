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
    for transaction in transactions:
        category = transaction[2].strip().lower()
        model = Transaction()
        model.transaction_date = transaction[0]
        model.account = transaction[1]
        if check_category_exist(category, session):
            model.category = session.add(Category(title=category))
        else:
            model.category = get_category_id(category, session)
        model.amount = abs(transaction[3])
        model.currency = transaction[4]
        model.converted_amount = abs(transaction[5])
        model.converted_currency = transaction[6]
        model.description = transaction[7]
        model.is_debet = (transaction[3] > 0)
        session.add(model)
    session.commit()
    session.close()


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
