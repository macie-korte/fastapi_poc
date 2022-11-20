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
@app.post("/fetcher/", status_code=status.HTTP_201_CREATED, response_model=schemas.FetcherRead)
def create_fetcher(fetcher: schemas.FetcherCreate, db: Session = Depends(get_db_session)):
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
        timelimit = fetcher.timelimit,
        mailbox = fetcher.mailbox,
        domains = fetcher.domains,
    )
    db.add(new_fetcher)
    db.commit()
    db.refresh(new_fetcher)
    return schemas.FetcherRead.from_orm(new_fetcher)

# Update an existing fetcher
@app.put("/fetcher/{fetcherid}/")
def update_fetcher(fetcherid: int, fetcher: schemas.FetcherCreate, db: Session = Depends(get_db_session)):
    fetcher_query = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid)
    try:
        existing_fetcher = fetcher_query.one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetch with ID {} was not found.".format(fetcherid))

    existing_fetcher.confname = fetcher.confname
    existing_fetcher.server = fetcher.server
    existing_fetcher.description = fetcher.description
    existing_fetcher.userid = fetcher.userid
    existing_fetcher.password = fetcher.password
    existing_fetcher.protocol = fetcher.protocol
    existing_fetcher.port = fetcher.port
    existing_fetcher.quickdelete = fetcher.quickdelete
    existing_fetcher.active = fetcher.active
    existing_fetcher.uidvalidkey = fetcher.uidvalidkey
    existing_fetcher.timelimit = fetcher.timelimit
    existing_fetcher.mailbox = fetcher.mailbox
    existing_fetcher.domains = fetcher.domains
    #fetcher_query.update(dict(fetcher))
    db.add(existing_fetcher)
    db.commit()

    #existing_fetcher = fetcher_query.one()
    db.refresh(existing_fetcher)
    return schemas.FetcherRead.from_orm(existing_fetcher)


# Get all fetchers
@app.get("/fetcher/", response_model=List[schemas.FetcherRead])
def retrieve_fetchers(db: Session = Depends(get_db_session)):
    fetchers = db.query(models.Fetcher).all()
    fetcher_schemas = [schemas.FetcherRead.from_orm(fetcher) for fetcher in fetchers]
    return fetcher_schemas


# Get a specific fetcher
# TODO: in the future change this to take ID when table is altered.
@app.get("/fetcher/{fetcherid}/", response_model=schemas.FetcherRead)
def retrieve_fetcher(fetcherid: int, db: Session = Depends(get_db_session)):
    try:
        fetcher = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetch with ID {} was not found.".format(fetcherid))
        # Or alternatively, alter the retrieve_fetcher function def to take response,
        # then substitute the above line with these:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'detail': "Fetch with ID {} was not found.".format(fetcherid)}
    return schemas.FetcherRead.from_orm(fetcher)

# Delete a fetcher
@app.delete("/fetcher/{fetcherid}", response_model=schemas.FetcherRead)
def delete_fetcher(fetcherid: int, db: Session = Depends(get_db_session)):
    try:
        fetcher = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetch with ID {} was not found.".format(fetcherid))

    db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid).delete()
    db.commit()
    return schemas.FetcherRead.from_orm(fetcher)  # to show the API user what was deleted for success messages & such.


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
