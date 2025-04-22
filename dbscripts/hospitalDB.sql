-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS hospital;

-- Use the database
USE hospital;

-- Create the users tableusers
CREATE TABLE IF NOT EXISTS charges (
  id    			INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  account_id        VARCHAR(50) NOT NULL,
  date              DATE NOT NULL,
  amount            NUMERIC(14,2) NOT NULL,
  merchant_name     VARCHAR(100),
  description       VARCHAR(100)
);

CREATE USER IF NOT EXISTS 'hospital_user'@'localhost' IDENTIFIED BY 'Pass123!';

-- Grant the user permissions on the medisave database
GRANT SELECT, INSERT, UPDATE, DELETE ON medisave.* TO 'hospital_user'@'localhost';