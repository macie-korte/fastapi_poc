from database import Base

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.types import Time
from sqlalchemy.orm import relationship


class Fetcher(Base):
    __tablename__ = "fetchers"

    fetcherid = Column(Integer, primary_key=True)
    confname = Column(String, nullable=False, unique=True)
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

    schedules = relationship("FetcherSchedule", back_populates="fetcher")

class FetcherSchedule(Base):
    __tablename__ = "fetcherschedules"

    fetcherscheduleid = Column(Integer, primary_key=True)
    fetcherid      = Column(Integer, ForeignKey("fetchers.fetcherid"), nullable=False)
    downtimedays   = Column(String, nullable=False)
    downtimestart  = Column(Time, nullable=False)
    downtimeend    = Column(Time, nullable=False)

    fetcher = relationship("Fetcher", back_populates="schedules")
