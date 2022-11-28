import datetime
from pydantic import BaseModel, Field
from typing import List

from pydanticutils import AllOptional

# Fetcher Schedules
class FetcherScheduleCreate(BaseModel):
    fetcherid: int = Field(alias='fetcher_id')
    downtimedays: str = Field(alias='downtime_days',
        example="0,1,2,3,4,5,6",
        description="a list of numbers, 0 - 6, where 0 represents Sunday and 6 represents Saturday.")
    downtimestart: datetime.time = Field(alias='downtime_start',
        example="08:15",
        description="Format: HH:MM given in the 24-hour clock")
    downtimeend: datetime.time = Field(alias='downtime_end',
        example="17:30",
        description="Format: HH:MM given in the 24-hour clock")

    # read the data even if it is not a dict, but an ORM model
    # (or any other arbitrary object with attributes)
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class FetcherScheduleRead(FetcherScheduleCreate):
    fetcherscheduleid: int = Field(alias='id')


# Fetchers
class FetcherCreate(BaseModel):
    confname: str = Field(alias='name')
    server: str | None
    description: str | None
    userid: str | None = Field(alias='username')
    password: str | None
    protocol: str | None
    port: int | None = Field(ge=1, le=65535)
    quickdelete: bool = Field(alias='quick_delete')
    active: bool
    timelimit: int | None = Field(alias='time_limit')
    mailbox: str
    domains: str | None

    # read the data even if it is not a dict, but an ORM model
    # (or any other arbitrary object with attributes)
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class FetcherPatch(FetcherCreate, metaclass=AllOptional):
    pass

class FetcherRead(FetcherCreate):
    fetcherid: int = Field(alias='id')
    schedules: List[FetcherScheduleRead] = []
    uidvalidkey: int | None = Field(alias='uid_validity_key')

