from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from src.config import db_settings

SQLALCHEMY_DB_URL = db_settings.db_url

engine = create_engine(SQLALCHEMY_DB_URL)


SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


SessionLocal = scoped_session(SessionFactory)
Base = declarative_base()

print("Database is ready!")