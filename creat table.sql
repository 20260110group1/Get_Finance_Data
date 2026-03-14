CREATE DATABASE macro_monitor;
USE macro_monitor;

CREATE TABLE economic_indicator (
    id INT AUTO_INCREMENT PRIMARY KEY,
    indicator_code VARCHAR(20),
    report_date DATE,
    index_value FLOAT,
    yoy_growth FLOAT,
    country VARCHAR(10)
);

CREATE TABLE exchange_rate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rate_date DATE,
    usd_twd FLOAT
);

CREATE TABLE economic_score (
    id INT AUTO_INCREMENT PRIMARY KEY,
    score_date DATE,
    
    cpi_score FLOAT,
    ppi_score FLOAT,
    fx_score FLOAT,
    
    total_score FLOAT,
    
    signal_light VARCHAR(10)
);