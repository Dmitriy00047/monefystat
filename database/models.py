from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Boolean, Integer, String, Date, DateTime
from datetime import datetime

Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
    transaction_date = Column('transaction_date', Date)
    account = Column('account', String)
    category = Column('category', String)
    amount = Column('amount', Float)
    currency = Column('currency', String)
    converted_amount = Column('converted_amount', Float)
    converted_currency = Column('converted_currency', String)
    description = Column('description', String)
    is_debet = Column('is_debet', Boolean)
