create database brandsense_db;

\c brandsense_db;

DROP TABLE logos;
CREATE TABLE IF NOT EXISTS logos(
  logo_id uuid DEFAULT uuid_generate_v4(),
  customer VARCHAR(50) NOT NULL,
  logo VARCHAR(50) NOT NULL,
  colors VARCHAR(50)[],
  text VARCHAR(50)[],
  link VARCHAR(300),
  info VARCHAR(1000),
  img BYTEA
);

INSERT INTO logos(logo_id, customer, logo, colors, text, link, info)
VALUES(uuid_generate_v4(), 'Nike', 'Nike', ARRAY ['deeppink', 'palevioletred', 'plum', 'white'], ARRAY[]::VARCHAR(50)[], 'https://www.nike.com/', 'Breast Cancer Awareness'),
(uuid_generate_v4(), 'Kroger', 'King Soopers', ARRAY ['yellow', 'crimson', 'white', 'darkorange'], ARRAY ['KING Soopers', 'KING', 'Soopers'], 'https://www.kingsoopers.com/', 'A store');

-- everything needed for history table
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TABLE userHistory;
CREATE TABLE IF NOT EXISTS userHistory(
  histID uuid DEFAULT uuid_generate_v4(),
  ts timestamp default now(),
  img BYTEA,
  url VARCHAR(300),
  logo VARCHAR(300),
  colors VARCHAR(50)[],
  text VARCHAR(50)[],
  username VARCHAR(50)
);

-- Users table with username as primary key
DROP TABLE users;
CREATE TABLE IF NOT EXISTS users(
  username VARCHAR(50) PRIMARY KEY,
  password VARCHAR(50)
);

INSERT INTO users(username, password) VALUES('ian', '123');
