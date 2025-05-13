from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)

class UserCoin(Base):
    __tablename__ = 'user_coins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    coin = Column(String(10), nullable=False)
    amount = Column(Numeric(18, 8), nullable=False)
    purchase_price = Column(Numeric(18, 8), nullable=False)

class PortfolioHistory(Base):
    __tablename__ = 'portfolio_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    total_value = Column(Numeric(18, 8), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
