""" Run this file as a script to start a uvicorn webserver running this API.
Visit http://localhost:8000/docs/ to see API documentation and to test running
the API calls.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Response
from sqlalchemy.orm  import Session
from sqlalchemy.exc import NoResultFound
from typing import List

import schemas
import models
from database import get_db_session

app = FastAPI()


# Create a new fetcher
@app.post("/fetcher/", status_code=status.HTTP_201_CREATED, response_model=List[schemas.Fetcher])
def create_fetcher(fetcher: schemas.Fetcher, db: Session = Depends(get_db_session)):
    new_fetcher = models.Fetcher(
        confname = fetcher.confname,
        server = fetcher.server,
        description = fetcher.description,
        userid = fetcher.userid,
        password = fetcher.password,
        protocol = fetcher.protocol,
        port = fetcher.port,
        quickdelete = fetcher.quickdelete,
        active = fetcher.active,
        uidvalidkey = fetcher.uidvalidkey,
        timelimit = fetcher.time_limit,
        mailbox = fetcher.mailbox,
        domains = fetcher.domains,
    )
    db.add(new_fetcher)
    db.commit()
    db.refresh(new_fetcher)
    return schemas.Fetcher.from_orm(new_fetcher)

# Update an existing fetcher
@app.put("/fetcher/{confname}/")
def update_fetcher(confname: str, fetcher: schemas.Fetcher, db: Session = Depends(get_db_session)):
    fetcher_query = db.query(models.Fetcher).filter(models.Fetcher.confname == confname)
    try:
        existing_fetcher = fetcher_query.one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetch with config name {} was not found.".format(confname))

    existing_fetcher.confname = fetcher.config_name
    existing_fetcher.server = fetcher.server
    existing_fetcher.description = fetcher.description
    existing_fetcher.userid = fetcher.username
    existing_fetcher.password = fetcher.password
    existing_fetcher.protocol = fetcher.protocol
    existing_fetcher.port = fetcher.port
    existing_fetcher.quickdelete = fetcher.quick_delete
    existing_fetcher.active = fetcher.active
    existing_fetcher.uidvalidkey = fetcher.uid_validity_key
    existing_fetcher.timelimit = fetcher.time_limit
    existing_fetcher.mailbox = fetcher.mailbox
    existing_fetcher.domains = fetcher.domains
    #fetcher_query.update(dict(fetcher))
    db.add(existing_fetcher)
    db.commit()

    return fetcher_query.one()


# Get all fetchers
@app.get("/fetcher/", response_model=List[schemas.Fetcher])
def retrieve_fetchers(db: Session = Depends(get_db_session)):
    fetchers = db.query(models.Fetcher).all()
    fetcher_schemas = [schemas.Fetcher.from_orm(fetcher) for fetcher in fetchers]
    return fetcher_schemas


# Get a specific fetcher
# TODO: in the future change this to take ID when table is altered.
@app.get("/fetcher/{confname}/", response_model=schemas.Fetcher)
def retrieve_fetcher(confname: str, db: Session = Depends(get_db_session)):
    try:
        fetcher = db.query(models.Fetcher).filter(models.Fetcher.confname == confname).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetch with config name {} was not found.".format(confname))
        # Or alternatively, alter the retrieve_fetcher function def to take response,
        # then substitute the above line with these:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'detail': "Fetch with config name {} was not found.".format(confname)}
    return schemas.Fetcher.from_orm(fetcher)

# Delete a fetcher
@app.delete("/fetcher/{confname}", response_model=schemas.Fetcher)
def delete_fetcher(confname: str, db: Session = Depends(get_db_session)):
    try:
        fetcher = db.query(models.Fetcher).filter(models.Fetcher.confname == confname).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetch with config name {} was not found.".format(confname))

    db.query(models.Fetcher).filter(models.Fetcher.confname == confname).delete()
    db.commit()
    return schemas.Fetcher.from_orm(fetcher)  # to show the API user what was deleted for success messages & such.


# emails = ["Order confirmation: #{}".format(i*3) for i in range(100)]

# NOTE: if you give FastAPI decorated functions kwargs that it doesn't recognize
# (like limit & offset below), it will automatically extract them from query
# params, if they are available there.
# @app.get("/email")
# def email(limit: int = 20, offset: int = 0):
#     try:
#         return emails[offset:offset+limit]
#     except IndexError:
#         try:
#             return emails[offset:]
#         except IndexError:
#             return []

# @app.get("/email/{emailid}")
# def email(emailid: int):
#     try:
#         return emails[emailid]
#     except IndexError:
#         raise HTTPException(status_code=404, detail="Email not found")


if __name__ == "__main__":
    # Run the API in a web server on localhost:8000.
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
