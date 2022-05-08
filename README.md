To run this project:

1.  Make sure Python 3.10+ is installed.
2.  Make sure pipx is installed, or pip3 if that is not possible.
3.  Install virtualenv
4.  Checkout this project - top level directory of fastapi_poc
5.  Cd to fastapi_poc
6.  Create a virtualenv for this project.  Run `virtualenv fastapi-env`.
7.  Activate your virtualenv: `source fastapi-env/bin/active`.
8.  Install the requirements: `pipx install -r requirements.txt` or `pip3 install -r requirements.txt`.

If you get a notification of any missing requirements, try running `pipx install -r requirements2.txt`.  That is more complete and was generated based on a pip-freeze of my local virtualenv instance, but it does include indirect requirements, not only direct requirements.
