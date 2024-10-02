from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from insightscapehub.utils.settings import DB_URL

SQLALCHEMY_DATABASE_URL = DB_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
