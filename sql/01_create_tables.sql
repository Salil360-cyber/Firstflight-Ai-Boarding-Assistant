-- FirstFlight · Step 1: create the 4 raw tables (run once in the "firstflight" database)
DROP VIEW  IF EXISTS sessions_clean CASCADE;
DROP TABLE IF EXISTS sessions_raw, agent_tickets, qa_reviews, contact_centre_contacts;

CREATE TABLE sessions_raw (
    session_id          TEXT,
    user_id             TEXT,
    started_at          TIMESTAMP,
    ended_at            TIMESTAMP,
    channel             TEXT,
    language            TEXT,
    passenger_type      TEXT,
    route_type          TEXT,
    topic               TEXT,
    app_version         TEXT,
    turns               INT,
    first_response_sec  NUMERIC(6,1),
    outcome             TEXT,
    handoff_reason      TEXT,
    csat                INT
);

CREATE TABLE agent_tickets (
    ticket_id         TEXT PRIMARY KEY,
    session_id        TEXT,
    created_at        TIMESTAMP,
    assigned_at       TIMESTAMP,
    closed_at         TIMESTAMP,
    topic             TEXT,
    handoff_reason    TEXT,
    agent_handle_min  NUMERIC(6,1),
    resolution        TEXT
);

CREATE TABLE qa_reviews (
    review_id    TEXT PRIMARY KEY,
    session_id   TEXT,
    reviewed_at  TIMESTAMP,
    app_version  TEXT,
    language     TEXT,
    topic        TEXT,
    verdict      TEXT,
    issue_type   TEXT
);

CREATE TABLE contact_centre_contacts (
    contact_id      TEXT PRIMARY KEY,
    contact_date    DATE,
    channel         TEXT,
    topic           TEXT,
    passenger_type  TEXT,
    handle_min      NUMERIC(6,1)
);
