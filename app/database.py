# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()
