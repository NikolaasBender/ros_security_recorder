CREATE TABLE recordings(
    id SERIAL PRIMARY KEY,
    pid INT DEFAULT -1,
    repeat BOOL NOT NULL,
    week_day INT[], -- Filled with values of 0-6 to denote what days of the week to record on
    start_date DATE NOT NULL,
    stop_date DATE,
    duration INTERVAL NOT NULL,
    start_time TIME NOT NULL,
    last_started TIMESTAMP,
    camera_topics TEXT[] NOT NULL
);