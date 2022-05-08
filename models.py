from database import Base

from sqlalchemy import Column, Integer, String, Boolean

class Fetcher(Base):
    __tablename__ = "fetchers"

    confname = Column(String, primary_key=True)
    server = Column(String, nullable=False)
    description = Column(String, nullable=False)
    userid = Column(String)
    password = Column(String)
    protocol = Column(String)
    port = Column(Integer)
    quickdelete = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    uidvalidkey = Column(Integer)
    timelimit = Column(Integer, default=15)
    mailbox = Column(String, nullable=False, default='inbox')
    domains = Column(String)
