# To run this project #

## First time setup ##

1.  Make sure Python 3.10+ is installed.  
    Any version earlier than 3.10 will raise syntax errors.
2.  Make sure pipx is installed, or pip3 if that is not possible.
3.  Install virtualenv
4.  Install sqlite (sqlite3 - only if you're working on a demo project
    and don't have access to an Archiver with a Postgers DB)
5.  Clone this git project - top level directory of fastapi_poc 
    (e.g. `git clone git@gitlab.intradyn.com:mkorte/fastapi_poc.git`)
6.  Cd to fastapi_poc
7.  Create a virtualenv for this project.  Run `virtualenv fastapi-env`.
8.  Install the requirements: `pipx install -r requirements.txt` or `pip3 install -r requirements.txt`.  
    If you get a notification of any missing requirements, try running `pipx install -r requirements2.txt`.  
    That is more complete and was generated based on a pip-freeze of my local virtualenv instance, 
    but it does include indirect requirements, not only direct requirements.

## Every time steps ##

5.  Cd to your fastapi_poc clone
7.  Activate your virtualenv: `source fastapi-env/bin/active`.
8.  Run the main program `python3 main.py`.  This will run a uvicorn server which will server the FastAPI APIs and documentation.
9.  The output will contain a line like `Uvicorn running on http://127.0.0.1:8000`.  
    In your browser visit http://127.0.0.1:8000/docs to see the API documentation.
    You can try out any API call here from the documentation page or you can call
    any of the APIs from an address like http://127.0.0.1:8000/fetcher/ from your own code.


## Other Helpful Info ##

* Run `sqlite3 sqlapp.db` to run ad hoc SQL queries.  This will eventually be replaced with Postgres.
* If `source fastapi-env/bin/active` does not work, then cd up a directory and try `source fastapi_poc/fastapi-env/bin/active` from there.
* Run tests by cding to your fastapi_poc directory and running `python -m pytest test_main.py -vv`
