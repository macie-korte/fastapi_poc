from pydantic import BaseModel, Field


class FetcherCreate(BaseModel):
    confname: str = Field(alias='name')
    server: str | None
    description: str | None
    userid: str | None = Field(alias='username')
    password: str | None
    protocol: str | None
    port: int | None
    quickdelete: bool = Field(alias='quick_delete')
    active: bool
    uidvalidkey: int | None = Field(alias='uid_validity_key')
    timelimit: int | None = Field(alias='time_limit')
    mailbox: str
    domains: str | None

    # read the data even if it is not a dict, but an ORM model
    # (or any other arbitrary object with attributes)
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class FetcherRead(FetcherCreate):
    fetcherid: int = Field(alias='id')
