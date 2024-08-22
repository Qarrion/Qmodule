
/* --------------------------------- create --------------------------------- */
CREATE TABLE test (
    id SERIAL PRIMARY KEY,
    num INTEGER,
    data TEXT,
    timez TIMESTAMPTZ NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT now()
)



/* --------------------------------- insert --------------------------------- */
INSERT INTO my_table (name, event_time) VALUES ('Eventc Name2', '2024-03-10 15:02:00+09:00');



/* --------------------------------- select --------------------------------- */
select * from test




/* --------------------------------- select --------------------------------- */
select id, num, data,
	timez AT TIME ZONE 'Asia/Seoul' as timez_kst,
	last_updated
	
	from test;