CREATE TABLE Fetchers (
  fetcherid     INTEGER PRIMARY KEY AUTOINCREMENT,
  confname      TEXT UNIQUE NOT NULL,          --  The name of the server
  server        TEXT NOT NULL,                 --  IP address or name of server
  description   TEXT,                          --  Description of the server
  userid        TEXT,                          --  Name of email account user
  password      TEXT,                          --  Password for account
  protocol      TEXT,                          --  IMAP, POP3, etc
  port          INTEGER,                       --  Port on which to connect
  quickdelete   BOOLEAN DEFAULT 'F',           --  Will the agent delete before archiving
  active        BOOLEAN DEFAULT 'T',           --  Is this server being checked
  uidvalidkey   INTEGER DEFAULT NULL,          --  Last good UIDVALIDITY or UIDL
  timelimit     INTEGER DEFAULT 15,            --  Hard email-fetch time limit, in minutes.
  mailbox       TEXT NOT NULL DEFAULT 'inbox', --  mailbox to fetch from (not used for POP)
  domains       TEXT                           --  domains expected from this fetcher
);

CREATE TABLE FetcherSchedules (
  fetcherscheduleid  INTEGER PRIMARY KEY AUTOINCREMENT,
  fetcherid       INTEGER NOT NULL
                      references fetchers
                      on delete cascade
                      on update cascade,
  downtimedays    TEXT NOT NULL,  -- TODO: for Postgresql should be an Array type.
  downtimestart   TIME NOT NULL,
  downtimeend     TIME NOT NULL
);

