-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS plaid;

-- Use the database
USE plaid;

-- Create the tables
-- 1. Users & Identity
CREATE TABLE IF NOT EXISTS users (
  user_id        VARCHAR(50) PRIMARY KEY,              -- your internal user identifier
  plaid_user_id  VARCHAR(100) UNIQUE,                   -- Plaid’s identifier for this end‐user
  full_name      VARCHAR(100),
  date_of_birth  DATE,
  mailing_address VARCHAR(100),
  email          VARCHAR(100) UNIQUE NOT NULL,
  phone_number   VARCHAR(100)
);

-- 2. Financial Institutions
CREATE TABLE IF NOT EXISTS institutions (
  institution_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  plaid_institution_id VARCHAR(100) UNIQUE,             -- Plaid’s institution ID
  name              VARCHAR(100) NOT NULL
);

-- 3. Accounts Metadata
CREATE TABLE IF NOT EXISTS accounts (
  account_id         VARCHAR(50) PRIMARY KEY,          -- Plaid’s account ID
  user_id            VARCHAR(50) NOT NULL
    REFERENCES users(user_id)
    ON DELETE CASCADE,
  institution_id     INT UNSIGNED NOT NULL
    REFERENCES institutions(institution_id),
  account_name       VARCHAR(100),
  account_type       VARCHAR(20),               -- e.g. checking, credit
  account_subtype    VARCHAR(50),               -- e.g. “savings”, “mortgage”
  ownership_type     VARCHAR(20),               -- single, joint
  mask               VARCHAR(10),               -- last few digits of acct#
  routing            VARCHAR(20)                -- routing or IBAN/BIC
);

-- 4. Balances (snapshot history if you want over time)
CREATE TABLE IF NOT EXISTS account_balances (
  balance_id      SERIAL PRIMARY KEY,
  account_id      VARCHAR(50) NOT NULL
    REFERENCES accounts(account_id),
  fetched_at      TIMESTAMP NOT NULL DEFAULT now(),
  current_balance NUMERIC(14,2),
  available_balance NUMERIC(14,2)
);

-- 5. Transactions
CREATE TABLE IF NOT EXISTS transactions (
  transaction_id    VARCHAR(50) PRIMARY KEY,           -- Plaid’s transaction ID
  account_id        VARCHAR(50) NOT NULL
    REFERENCES accounts(account_id),
  date              DATE NOT NULL,
  amount            NUMERIC(14,2) NOT NULL,
  merchant_name     VARCHAR(100),
  category          VARCHAR(100),                     -- Plaid often returns an array of categories
  running_balance   NUMERIC(14,2),              -- optional
  pending           BOOLEAN NOT NULL DEFAULT FALSE,
  description       VARCHAR(100)
);

-- 6. Credit & Loan Details
CREATE TABLE IF NOT EXISTS credit_loan_details (
  credit_id          VARCHAR(50) PRIMARY KEY,          -- same as account_id if you prefer
  account_id         VARCHAR(50) UNIQUE NOT NULL
    REFERENCES accounts(account_id),
  outstanding_balance NUMERIC(14,2),
  credit_limit        NUMERIC(14,2),
  apr                 NUMERIC(5,3),             -- e.g. 0.159 = 15.9%
  minimum_payment     NUMERIC(14,2),
  next_due_date       DATE,
  original_amount     NUMERIC(14,2),
  maturity_date       DATE
);

-- 6b. Credit payment history (if you need multiple payments)
CREATE TABLE IF NOT EXISTS credit_payments (
  payment_id     SERIAL PRIMARY KEY,
  credit_id      VARCHAR(50) NOT NULL
    REFERENCES credit_loan_details(credit_id),
  payment_date   DATE NOT NULL,
  amount         NUMERIC(14,2) NOT NULL,
  status         VARCHAR(20)                   -- on‑time, late, etc.
);

-- 7. Investment Accounts
CREATE TABLE IF NOT EXISTS investment_accounts (
  inv_account_id   VARCHAR(50) PRIMARY KEY,            -- Plaid’s account ID
  account_id       VARCHAR(50) UNIQUE NOT NULL
    REFERENCES accounts(account_id),
  account_type     VARCHAR(50)                  -- brokerage, 401k, etc.
);

-- 7b. Investment Holdings
CREATE TABLE IF NOT EXISTS investment_holdings (
  holding_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  inv_account_id   VARCHAR(50) NOT NULL
    REFERENCES investment_accounts(inv_account_id),
  asset_type       VARCHAR(50),                 -- stock, ETF, bond, etc.
  symbol           VARCHAR(20),
  quantity         NUMERIC(16,6),
  market_value     NUMERIC(14,2),
  cost_basis       NUMERIC(14,2),
  date_acquired    DATE
);

-- 7c. Investment transaction history
CREATE TABLE IF NOT EXISTS investment_transactions (
  inv_tx_id        VARCHAR(50) PRIMARY KEY,            -- Plaid’s investment transaction ID
  holding_id       INT UNSIGNED NOT NULL
    REFERENCES investment_holdings(holding_id),
  tx_date          DATE NOT NULL,
  tx_type          VARCHAR(20),                 -- buy, sell, dividend, etc.
  quantity         NUMERIC(16,6),
  amount           NUMERIC(14,2)
);

-- Replace 'medisave_user' and 'StrongPassword123!' with your desired username and password
CREATE USER IF NOT EXISTS 'plaid_user'@'localhost' IDENTIFIED BY 'Pass123!';

-- Grant the user permissions on the medisave database
GRANT SELECT, INSERT, UPDATE, DELETE ON plaid.* TO 'plaid_user'@'localhost';
