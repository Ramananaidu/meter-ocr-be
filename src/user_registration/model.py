from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Float

from src.user_registration.settings import Base, engine


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), index=True)
    password = Column(String(255), index=True)
    email = Column(String(50), index=True)
    phone_number = Column(String(15), index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    create_date = Column(DateTime, default=datetime.now())
    update_date = Column(DateTime)
    token = Column(String(255), index=True)
    token_date = Column(DateTime)
    embedding = Column(ARRAY(Float))
    


class UserAuth(Base):
    __tablename__ = 'user_auth'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, unique=True)
    name = Column(String(255), index=True)
    pho_no = Column(Integer)


Base.metadata.create_all(bind=engine)
