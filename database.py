from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DB_URL = 'postgresql+psycopg2://postgres:@172.16.155.129/cvxthree'

# "check_same_thread": False is as recommended by FastAPI.
engine = create_engine(SQLALCHEMY_DB_URL)  #, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
