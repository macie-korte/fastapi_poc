"""
Run like so:

`python3 -m pytest test_main.py`


"""

from fastapi.testclient import TestClient

from main import app
from database import get_db_session
import models
import pytest

client = TestClient(app)

# This is a hack to empty out the DB which won't work for large-scale testing
# with tons of tables.
# TODO: replace with something similar to our cvxthree drop & recreate all tables logic.
@pytest.fixture()
def test_db():
    db = next(get_db_session())
    db.query(models.Fetcher).delete()
    db.query(models.FetcherSchedule).delete()
    db.execute("delete from sqlite_sequence where name='Fetchers';")
    db.execute("delete from sqlite_sequence where name='FetcherSchedules';")
    db.commit()
    yield
    db.close()


############################# GET list tests #################################
def test_get_fetcher_list_when_none_exist(test_db):
    """
     * GET /fetcher/ returns an empty list before any fetchers have been added
       to the DB.
    """
    response = client.get("/fetcher/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_fetcher_list_when_some_exist(test_db):
    """
     * POST /fetcher/ called twice creates two fetcher records.
     * GET /fetcher/ returns an list of fetchers which have been added to the DB.
    """
    # POST /fetcher/ called twice creates two fetcher record.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 1

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox.foo.com",
          "description": "Fetch from Foos journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 2

    # GET /fetcher/ then gets the list of 2 fetchers.
    response = client.get("/fetcher/")
    assert response.status_code == 200
    assert response.json() == [{
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          'schedules': [],
          "active": True,
          "uid_validity_key": None,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None,
          "id": 1
        }, {
          "name": "fetcher02",
          "server": "mailbox.foo.com",
          "description": "Fetch from Foos journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          'schedules': [],
          "active": True,
          "uid_validity_key": None,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None,
          "id": 2
        },]

############################ GET fetcher tests ################################
def test_get_fetcher_nonexistant_id(test_db):
    """
     * GET /fetcher/ returns an empty list before any fetchers have been
       added to the DB.
    """
    response = client.get("/fetcher/3/")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Fetcher with ID 3 was not found.'}

# No need to test a regular GET: I do it in almost every other test.

############################ POST create tests ################################
def test_create_fetcher(test_db):
    """
     * POST /fetcher/ creates one fetcher record when good data is POSTed.
     * GET /fetcher/1/ can then retrieve the fetcher which was created.
    """
    # POST /fetcher/ creates one fetcher record when good data is POSTed.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201

    expected_json = {
        "name": "fetcher02",
        "server": "mailbox.intradyn.com",
        "description": "Fetch from Intradyns journaling mailbox",
        "username": "macie",
        "password": "123abc",
        "protocol": "IMAP4",
        "port": 143,
        "quick_delete": True,
        "schedules": [],
        "active": True,
        "uid_validity_key": None,
        "time_limit": 0,
        "mailbox": "INBOX",
        "domains": None,
        "id": 1
        }

    assert response.json() == expected_json

    # GET /fetcher/1/ can then retrieve the fetcher which was created.
    response = client.get("/fetcher/1/")
    assert response.status_code == 200
    assert response.json() == expected_json

def test_create_fetcher_repeat_name(test_db):
    """
    * POST /fetcher/ creates one fetcher record when good data is POSTed.
    * POST /fetcher/ when called again with the same config name fails.
    """
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "uid_validity_key": 0,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "uid_validity_key": 0,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 500
    assert response.json() == {'detail': "Configuration name 'fetcher01' is already used by another fetcher."}

############################ PUT update tests ################################
def test_update_fetcher(test_db):
    """
     * POST /fetcher/ creates one fetcher record when good data is POSTed.
     * PUT /fetcher/1/ updates the given fetcher.
     * GET /fetcher/1/ can then retrieve the fetcher which was created.
    """
    # POST /fetcher/ creates one fetcher record when good data is POSTed.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201

    # PUT /fetcher/1/ updates the given fetcher.
    response = client.put("/fetcher/1/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.foo.com",
          "description": "Fetch from Foos journaling mailbox",
          "username": "mkorte",
          "password": "Intradyn123",
          "protocol": "POP3",
          "port": 993,
          "quick_delete": True,
          "schedules": [],
          "active": True,
          "uid_validity_key": None,
          "time_limit": 0,
          "mailbox": "Inbox",
          "domains": None
        })

    expected_json = {
          "name": "fetcher01",
          "server": "mailbox.foo.com",
          "description": "Fetch from Foos journaling mailbox",
          "username": "mkorte",
          "password": "Intradyn123",
          "protocol": "POP3",
          "port": 993,
          "quick_delete": True,
          "schedules": [],
          "active": True,
          "uid_validity_key": None,
          "time_limit": 0,
          "mailbox": "Inbox",
          "domains": None,
          "id": 1
        }

    assert response.json() == expected_json

    # GET /fetcher/1/ can then retrieve the fetcher which was created.
    response = client.get("/fetcher/1/")
    assert response.status_code == 200
    assert response.json() == expected_json

def test_put_fetcher_nonexistant_id(test_db):
    """
    * PUT on /fetcher/3/ returns a 404 since fetcher 3 does not exist.
    """
    response = client.put("/fetcher/3/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.foo.com",
          "description": "Fetch from Foos journaling mailbox",
          "username": "mkorte",
          "password": "Intradyn123",
          "protocol": "POP3",
          "port": 993,
          "quick_delete": True,
          "active": True,
          "uid_validity_key": 0,
          "time_limit": 0,
          "mailbox": "Inbox",
          "domains": None
        })

    assert response.status_code == 404
    assert response.json() == {'detail': 'Fetcher with ID 3 was not found.'}

############################## DELETE tests ##################################
def test_delete_fetcher(test_db):
    """
     * POST /fetcher/ called twice creates two fetcher records.
     * DELETE /fetcher/1/ then deletes the first fetcher which was created.
     * GET /fetcher/ then gets the list of fetchers which is now 1 fetcher.
    """
    # POST /fetcher/ called twice creates two fetcher record.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 1

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox.foo.com",
          "description": "Fetch from Foos journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 2

    # DELETE /fetcher/1/ then deletes the first fetcher which was created.
    response = client.delete("/fetcher/1/")
    assert response.status_code == 200

    expected_json = {
        "name": "fetcher01",
        "server": "mailbox.intradyn.com",
        "description": "Fetch from Intradyns journaling mailbox",
        "username": "macie",
        "password": "123abc",
        "protocol": "IMAP4",
        "port": 143,
        "quick_delete": True,
        "schedules": [],
        "active": True,
        "uid_validity_key": None,
        "time_limit": 0,
        "mailbox": "INBOX",
        "domains": None,
        "id": 1
        }

    assert response.json() == expected_json

    # GET /fetcher/ then gets the list of fetchers which is now 1 fetcher.
    response = client.get("/fetcher/")
    assert response.status_code == 200
    assert response.json() == [{
          "name": "fetcher02",
          "server": "mailbox.foo.com",
          "description": "Fetch from Foos journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "schedules": [],
          "active": True,
          "uid_validity_key": None,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None,
          "id": 2
        },]

def test_delete_fetcher_nonexistant_id(test_db):
    """
    * PUT on /fetcher/3/ returns a 404 since fetcher 3 does not exist.
    """
    response = client.delete("/fetcher/3/")

    assert response.status_code == 404
    assert response.json() == {'detail': 'Fetcher with ID 3 was not found.'}


########################## Batch Operation tests ##############################
def test_batch_delete(test_db):
    # First, create 3 fetchers
    # POST /fetcher/ creates one fetcher record.  Call it 3x.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 1

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox2.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 2

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher03",
          "server": "mailbox3.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 3

    # IDs to delete includes 2 of the 3 fetchers and one ID which doesn't exist.
    ids_to_delete = [1,3,5]

    # Expected Behavior:
    # * 2 of the 3 fetchers (1 & 3) which were included in the list are deleted.
    # * The other fetcher (2) does not get deleted.
    # * The non-existent ID (5) is ignored silently.
    response = client.post("/fetcher:delete/",
        json = {
            "ids": ids_to_delete
        })

    assert response.status_code == 200

    # GET /fetcher/ then gets the list of fetchers which is now 1 fetcher.
    response = client.get("/fetcher/")
    remaining_ids = [fetcher['id'] for fetcher in response.json()]
    assert remaining_ids == [2,]

def test_batch_activate_fetchers(test_db):
    # First, create 3 fetchers
    # POST /fetcher/ creates one fetcher record.  Call it 3x.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 1

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox2.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": False,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 2

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher03",
          "server": "mailbox3.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": False,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 3

    # IDs to activate includes 2 of the 3 fetchers and one ID which doesn't exist.
    ids_to_activate = [1,2,5]

    # Expected Behavior:
    # * 2 of the 3 fetchers (1 & 2) which were included in the list are activated.
    # * The other fetcher (3) does not get activated.
    # * The non-existent ID (5) is ignored silently.
    response = client.post("/fetcher:activate/",
        json = {
            "ids": ids_to_activate
        })

    assert response.status_code == 200

    # GET /fetcher/ then gets the list of fetchers which is now 1 fetcher.
    response = client.get("/fetcher/")
    assert [fetcher['active'] for fetcher in response.json() if fetcher['id'] == 1][0] == True
    assert [fetcher['active'] for fetcher in response.json() if fetcher['id'] == 2][0] == True
    assert [fetcher['active'] for fetcher in response.json() if fetcher['id'] == 3][0] == False

def test_batch_deactivate_fetchers(test_db):
        # First, create 3 fetchers
    # POST /fetcher/ creates one fetcher record.  Call it 3x.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": False,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 1

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox2.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 2

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher03",
          "server": "mailbox3.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 3

    # IDs to activate includes 2 of the 3 fetchers and one ID which doesn't exist.
    ids_to_activate = [1,2,5]

    # Expected Behavior:
    # * 2 of the 3 fetchers (1 & 2) which were included in the list are activated.
    # * The other fetcher (3) does not get activated.
    # * The non-existent ID (5) is ignored silently.
    response = client.post("/fetcher:deactivate/",
        json = {
            "ids": ids_to_activate
        })

    assert response.status_code == 200

    # GET /fetcher/ then gets the list of fetchers which is now 1 fetcher.
    response = client.get("/fetcher/")
    assert [fetcher['active'] for fetcher in response.json() if fetcher['id'] == 1][0] == False
    assert [fetcher['active'] for fetcher in response.json() if fetcher['id'] == 2][0] == False
    assert [fetcher['active'] for fetcher in response.json() if fetcher['id'] == 3][0] == True

def test_restart_deactivate_fetchers(test_db):
    # First, create 3 fetchers
    # POST /fetcher/ creates one fetcher record.  Call it 3x.
    response = client.post("/fetcher/",
        json = {
          "name": "fetcher01",
          "server": "mailbox.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 1

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher02",
          "server": "mailbox2.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 2

    response = client.post("/fetcher/",
        json = {
          "name": "fetcher03",
          "server": "mailbox3.intradyn.com",
          "description": "Fetch from Intradyns journaling mailbox",
          "username": "macie",
          "password": "123abc",
          "protocol": "IMAP4",
          "port": 143,
          "quick_delete": True,
          "active": True,
          "time_limit": 0,
          "mailbox": "INBOX",
          "domains": None
        })

    assert response.status_code == 201
    assert response.json()['id'] == 3

    # IDs to activate includes 2 of the 3 fetchers and one ID which doesn't exist.
    ids_to_activate = [1,3,5]

    # Expected Behavior:
    # * 2 of the 3 fetchers (1 & 3) which were included in the list are restarted.
    # * The other fetcher (2) does not get restarted.
    # * The non-existent ID (5) is ignored silently.
    response = client.post("/fetcher:restart/",
        json = {
            "ids": ids_to_activate
        })

    assert response.status_code == 200
    # TODO: not sure if there's anything I will be able to test in the future to
    # ensure this function actually restarts anything.


# TODO: add tests related to CRUDING fetcher schedules
# TODO: add tests related to returning fetcher schedules in the GET fetcher payload
# TODO: add tests related to order_by param on fetchers.
