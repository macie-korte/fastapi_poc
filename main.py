""" Run this file as a script to start a uvicorn webserver running this API.
Visit http://localhost:8000/docs/ to see API documentation and to test running
the API calls.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm  import Session
from sqlalchemy.exc import NoResultFound

import schemas
import sqlalchemy
import models
from database import get_db_session

app = FastAPI()

# Cross-origin resource sharing: allow requests from other hosts & ports
origins = [
    "http://localhost:4200"  # Our Angular POC port
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

################################## Fetchers ###################################
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
        timelimit = fetcher.timelimit,
        mailbox = fetcher.mailbox,
        domains = fetcher.domains,
    )
    # db.add(new_fetcher)
    # db.commit()
    # db.refresh(new_fetcher)
    # return schemas.FetcherRead.from_orm(new_fetcher)
    try:
        db.add(new_fetcher)
        db.commit()
        db.refresh(new_fetcher)
        return schemas.FetcherRead.from_orm(new_fetcher)
    except sqlalchemy.exc.IntegrityError as exc:
        if 'confname' in str(exc):
            raise HTTPException(status_code=500,
                detail="Configuration name '{}' is already used by another fetcher.".format(fetcher.confname))

# Update an existing fetcher
@app.put("/fetcher/{fetcherid}/")
def update_fetcher(fetcherid: int, fetcher: schemas.FetcherCreate, db: Session = Depends(get_db_session)):
    fetcher_query = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid)
    try:
        existing_fetcher = fetcher_query.one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher with ID {} was not found.".format(fetcherid))

    existing_fetcher.confname = fetcher.confname
    existing_fetcher.server = fetcher.server
    existing_fetcher.description = fetcher.description
    existing_fetcher.userid = fetcher.userid
    existing_fetcher.password = fetcher.password
    existing_fetcher.protocol = fetcher.protocol
    existing_fetcher.port = fetcher.port
    existing_fetcher.quickdelete = fetcher.quickdelete
    existing_fetcher.active = fetcher.active
    existing_fetcher.timelimit = fetcher.timelimit
    existing_fetcher.mailbox = fetcher.mailbox
    existing_fetcher.domains = fetcher.domains
    #fetcher_query.update(dict(fetcher))
    db.add(existing_fetcher)
    db.commit()
    db.refresh(existing_fetcher)
    return schemas.FetcherRead.from_orm(existing_fetcher)

# Partially update an existing fetcher
@app.patch("/fetcher/{fetcherid}/")
def update_fetcher(fetcherid: int, fetcher: schemas.FetcherPatch, db: Session = Depends(get_db_session)):
    fetcher_query = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid)
    try:
        existing_fetcher = fetcher_query.one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher with ID {} was not found.".format(fetcherid))

    if fetcher.confname is not None:
        existing_fetcher.confname = fetcher.confname
    if fetcher.server is not None:
        existing_fetcher.server = fetcher.server
    if fetcher.description is not None:
        existing_fetcher.description = fetcher.description
    if fetcher.userid is not None:
        existing_fetcher.userid = fetcher.userid
    if fetcher.password is not None:
        existing_fetcher.password = fetcher.password
    if fetcher.protocol is not None:
        existing_fetcher.protocol = fetcher.protocol
    if fetcher.port is not None:
        existing_fetcher.port = fetcher.port
    if fetcher.quickdelete is not None:
        existing_fetcher.quickdelete = fetcher.quickdelete
    if fetcher.active is not None:
        existing_fetcher.active = fetcher.active
    if fetcher.timelimit is not None:
        existing_fetcher.timelimit = fetcher.timelimit
    if fetcher.mailbox is not None:
        existing_fetcher.mailbox = fetcher.mailbox
    if fetcher.domains is not None:
        existing_fetcher.domains = fetcher.domains

    db.add(existing_fetcher)
    db.commit()
    db.refresh(existing_fetcher)
    return schemas.FetcherRead.from_orm(existing_fetcher)


# TODO: eventually move this and query param definition to fastapiutils
from enum import Enum
from fastapi import Query
class FetcherOrderEnum(str, Enum):
    name      = "name"
    name_asc  = "name asc"
    name_desc = "name desc"
    server      = "server"
    server_asc  = "server asc"
    server_desc = "server desc"
    protocol      = "protocol"
    protocol_asc  = "protocol asc"
    protocol_desc = "protocol desc"
    active      = "active"
    active_asc  = "active asc"
    active_desc = "active desc"

def get_order_by_dicts(order_by_query_vals, field_to_column_map):
    order_by_dicts = []
    for order_by_val in order_by_query_vals:
        try:
            order_by_val = order_by_val.value  # extract the string from an enum value.
        except AttributeError:
            pass  # assume order_by_val is already a string.

        try:
            field, direction = order_by_val.rsplit(" ", 1)
        except ValueError:
            field = order_by_val
            direction = "asc"

        if direction not in ["asc", "desc"]:
            raise ValueError("Direction must be asc or desc, but it was {} instead.".format(direction))

        try:
            column = field_to_column_map[field]
        except KeyError:
            raise ValueError("The field {} has no column mapping".format(field))

        order_by_dict = {
            "field": field,
            "direction": direction,
            "column": column
        }
        order_by_dicts.append(order_by_dict)
    return order_by_dicts

def add_order_by_clause(select_query, order_by_query_vals, field_to_column_map):
    """
    Takes an existing select_query and adds an order_by clause to it based on
    the passed in order_by_query_vals and field_to_column_map.

    @param order_by_query_vals: A list as returned by a FastAPI query param
        Example: ["name asc", "active desc", "protocol"]
    @param field_to_column_map: a dictionary that maps field names to table
        columns.
        Example: {
            "name": models.Fetcher.confname,
            "active": models.Fetcher.active
        }
    """
    order_by_dicts = get_order_by_dicts(order_by_query_vals, field_to_column_map)
    order_list = []
    for order_by_dict in order_by_dicts:
        if order_by_dict['direction'] == 'desc':
            select_query = select_query.order_by(order_by_dict['column'].desc())
        else:
            select_query = select_query.order_by(order_by_dict['column'].asc())
    return select_query
# End code to move to fastapiutils, but include a factory to create the Query below.

# Get all fetchers
@app.get("/fetcher/", response_model=list[schemas.FetcherRead])
def retrieve_fetchers(db: Session = Depends(get_db_session),
        order_by: list[FetcherOrderEnum] | None = Query(
            default=None,
            description=("Specifies which fields to sort the fetcher list by "
                "and whether to sort in ascending or descending orders.  "
                "Allowed sortable fields are 'name', 'server', 'protocol', and 'active'.  "
                "If sort order is not specified it is assumed to be ascending."
                "Example: `?order_by=active asc, name desc`"))):

    if order_by is None:
        order_by = ["active desc", "name asc"]

    field_to_column_map = {
        "name": models.Fetcher.confname,
        "server": models.Fetcher.server,
        "protocol": models.Fetcher.protocol,
        "active": models.Fetcher.active
    }
    fetcher_query = db.query(models.Fetcher)
    fetcher_query = add_order_by_clause(fetcher_query, order_by, field_to_column_map)
    fetchers = fetcher_query.all()
    fetcher_schemas = [schemas.FetcherRead.from_orm(fetcher) for fetcher in fetchers]
    return fetcher_schemas

# Get a specific fetcher
@app.get("/fetcher/{fetcherid}/", response_model=schemas.FetcherRead)
def retrieve_fetcher(fetcherid: int, db: Session = Depends(get_db_session)):
    try:
        fetcher = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher with ID {} was not found.".format(fetcherid))
    return schemas.FetcherRead.from_orm(fetcher)

# Restart a fetcher
@app.post("/fetcher/{fetcherid}:restart/", description="Restarts a fetcher if it is running, else noop.")
def restart_fetcher(fetcherid: int, db: Session = Depends(get_db_session)):
    try:
        fetcher = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher with ID {} was not found.".format(fetcherid))

    return "Successfully restarted fetcher '{}'.".format(fetcher.confname)

# Delete a fetcher
@app.delete("/fetcher/{fetcherid}/", response_model=schemas.FetcherRead)
def delete_fetcher(fetcherid: int, db: Session = Depends(get_db_session)):
    try:
        fetcher = db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher with ID {} was not found.".format(fetcherid))

    deletable_fetcher = schemas.FetcherRead.from_orm(fetcher)
    db.query(models.Fetcher).filter(models.Fetcher.fetcherid == fetcherid).delete()
    db.commit()
    return deletable_fetcher  # to show the API user what was deleted for success messages & such.


##################### Customer Batch Fetcher Operations #######################
# a batch operation call for restarting fetchers.
@app.post("/fetcher:restart/", description="""
    Restarts any listed fetchers

    Silently ignores any fetchers in the list which are disabled, not running or
    which do not exist.

    If successful, the response body is empty.
    """)
def restart_fetchers(fetcher_ids: schemas.BatchFetcherIds, db: Session = Depends(get_db_session)):
    # TODO: fill out later once on a real running system.
    pass

# a batch operation call for activating and deactivating fetchers.
@app.post("/fetcher:activate/", description="""
    Activates any active fetchers in the list

    Silently ignores any fetchers in the list which are already active or
    which do not exist.

    If successful, the response body is empty.
    """)
def activate_fetchers(fetcher_ids: schemas.BatchFetcherIds, db: Session = Depends(get_db_session)):
    db.query(models.Fetcher).filter(
        models.Fetcher.fetcherid.in_(fetcher_ids.ids)).update({models.Fetcher.active: True})

    db.commit()

@app.post("/fetcher:deactivate/", description="""
    Deactivates any active fetchers in the list

    Silently ignores any fetchers in the list which are already disabled or
    which do not exist.

    If successful, the response body is empty.
    """)
def deactivate_fetchers(fetcher_ids: schemas.BatchFetcherIds, db: Session = Depends(get_db_session)):
    db.query(models.Fetcher).filter(
        models.Fetcher.fetcherid.in_(fetcher_ids.ids)).update({models.Fetcher.active: False})

    db.commit()

# a batch operation to call for deleting fetchers.
@app.post("/fetcher:delete/", description="""
    Deletes many fetchers by fetcher ID.

    Silently ignores any fetchers in the list which are already deleted or
    never existed in the first place.

    If successful, the response body is empty.
    """)
def delete_fetchers(fetcher_ids: schemas.BatchFetcherIds, db: Session = Depends(get_db_session)):
    db.query(models.Fetcher).filter(models.Fetcher.fetcherid.in_(fetcher_ids.ids)).delete()
    db.commit()


############################# Fetcher Schedules ###############################
# Create a new fetcher
@app.post("/fetcherschedule/", status_code=status.HTTP_201_CREATED, response_model=schemas.FetcherScheduleRead)
def create_fetcherschedule(schedule: schemas.FetcherScheduleCreate, db: Session = Depends(get_db_session)):
    new_schedule = models.FetcherSchedule(
        fetcherid = schedule.fetcherid,
        downtimedays = schedule.downtimedays,
        downtimestart = schedule.downtimestart,
        downtimeend = schedule.downtimeend,
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return schemas.FetcherScheduleRead.from_orm(new_schedule)

# Update an existing fetcher
@app.put("/fetcherschedule/{fetcherscheduleid}/")
def update_fetcherschedule(fetcherscheduleid: int, schedule: schemas.FetcherScheduleCreate, db: Session = Depends(get_db_session)):
    schedule_query = db.query(models.FetcherSchedule).filter(models.FetcherSchedule.fetcherscheduleid == fetcherscheduleid)
    try:
        existing_schedule = schedule_query.one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher schedule with ID {} was not found.".format(fetcherscheduleid))

    existing_schedule.fetcherid = schedule.fetcherid
    existing_schedule.downtimedays = schedule.downtimedays
    existing_schedule.downtimestart = schedule.downtimestart
    existing_schedule.downtimeend = schedule.downtimeend

    db.add(existing_schedule)
    db.commit()
    db.refresh(existing_schedule)
    return schemas.FetcherScheduleRead.from_orm(existing_schedule)


# Get all fetchers
@app.get("/fetcherschedule/", response_model=list[schemas.FetcherScheduleRead])
def retrieve_fetcherschedules(db: Session = Depends(get_db_session)):
    schedules = db.query(models.FetcherSchedule).all()
    fetcher_schedule_schemas = [schemas.FetcherScheduleRead.from_orm(schedule) for schedule in schedules]
    return fetcher_schedule_schemas


# Get a specific fetcher
@app.get("/fetcherschedule/{fetcherscheduleid}/", response_model=schemas.FetcherScheduleRead)
def retrieve_fetcherschedule(fetcherscheduleid: int, db: Session = Depends(get_db_session)):
    try:
        schedule = db.query(models.FetcherSchedule).filter(models.FetcherSchedule.fetcherscheduleid == fetcherscheduleid).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher Schedule with ID {} was not found.".format(fetcherscheduleid))
    return schemas.FetcherScheduleRead.from_orm(schedule)

# Delete a fetcher
@app.delete("/fetcherschedule/{fetcherscheduleid}/", response_model=schemas.FetcherScheduleRead)
def delete_fetcherschedule(fetcherscheduleid: int, db: Session = Depends(get_db_session)):
    try:
        schedule = db.query(models.FetcherSchedule).filter(models.FetcherSchedule.fetcherscheduleid == fetcherscheduleid).one()
    except NoResultFound:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Fetcher Schedule with ID {} was not found.".format(fetcherscheduleid))

    db.query(models.FetcherSchedule).filter(models.FetcherSchedule.fetcherscheduleid == fetcherscheduleid).delete()
    db.commit()
    return schemas.FetcherScheduleRead.from_orm(schedule)  # to show the API user what was deleted for success messages & such.


if __name__ == "__main__":
    # Run the API in a web server on localhost:8000.
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
