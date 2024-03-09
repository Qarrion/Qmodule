

CREATE TABLE IF NOT EXISTS raw_trade_data(
    time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    symbol TEXT NOT NULL,   
    price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL
);

select create_hypertable('raw_trade_data', 'time');