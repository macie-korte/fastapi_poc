from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


USE_SQLITE = True


if USE_SQLITE:
    ### SQLite Settings ###
    SQLALCHEMY_DB_URL = "sqlite:///./sqlapp.db"
    # "check_same_thread": False is as recommended by FastAPI for SQLite only
    engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread": False})
else:
    ### Postgres Settings ###
    SQLALCHEMY_DB_URL = 'postgresql+psycopg2://postgres:@172.16.155.129/cvxthree'
    engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
