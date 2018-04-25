from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Boolean, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, autoincrement=True, primary_key=True)
    timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
    title = Column('title', String(255), nullable=False, unique=True)
    limit = Column('limit', Float, nullable=True)
    start_date = Column('start_date', Date, nullable=True)
    period = Column('period', Integer, nullable=True)
    is_repeated = Column('is_repeated', Boolean, nullable=True)
    transaction = relationship("Transaction")


class Transaction(Base):
    __tablename__ = "transaction"
    __table_args__ = (
        UniqueConstraint('date', 'account', 'amount', 'description', name='tr_constraint'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
    transaction_date = Column('transaction_date', Date)
    account = Column('account', String)
    category = Column('category', Integer, ForeignKey('category.id'))
    amount = Column('amount', Float)
    currency = Column('currency', String)
    converted_amount = Column('converted_amount', Float)
    converted_currency = Column('converted_currency', String)
    description = Column('description', String, nullable=True)
    is_debet = Column('is_debet', Boolean)
