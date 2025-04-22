-- 1) One user
INSERT INTO users 
  (user_id, plaid_user_id, full_name, date_of_birth, mailing_address, email, phone_number)
VALUES
  (1, 'plaid_user_abc123', 'John Doe', '1980-05-15', '123 Maple St, Orlando, FL 32801', 
   'john.doe@example.com', '555-123-4567');

-- 2) Institutions
INSERT INTO institutions (institution_id, plaid_institution_id, name) VALUES
  (1, 'ins_1001', 'Bank of America'),
  (2, 'ins_2002', 'Chase'),
  (3, 'ins_3003', 'Robinhood');

-- 3) Accounts for that user
INSERT INTO accounts 
  (account_id, user_id, institution_id, account_name, account_type, account_subtype, ownership_type, mask, routing)
VALUES
  -- Checking & Savings at BoA
  (101, 1, 1, 'My Checking',   'depository', 'checking', 'single', '1234', '110000000'),
  (102, 1, 1, 'My Savings',    'depository', 'savings',  'single', '5678', '110000000'),
  -- Credit card at Chase
  (103, 1, 2, 'Rewards Card',  'credit',     'credit card','single', '4321', NULL),
  -- 401(k) at Robinhood
  (104, 1, 3, 'Retirement',    'investment', '401k',     'single', 'N/A',  NULL);

-- 4) Balances (snapshot as of 2025‑04‑19 08:00)
INSERT INTO account_balances 
  (balance_id, account_id, fetched_at,          current_balance, available_balance)
VALUES
  (1,          101,        '2025-04-19 08:00:00', 2500.00,         2400.00),
  (2,          102,        '2025-04-19 08:00:00',10000.00,        10000.00);

-- 5) Some transactions on the checking account
INSERT INTO transactions 
  (transaction_id, account_id, date,       amount,   merchant_name,  category, running_balance, pending, description)
VALUES
  ('a1111111-1111-1111-1111-111111111111', 101, '2025-04-18', -75.50, 'Whole Foods', 'Groceries', 2575.50, FALSE, 'Grocery shopping'),
  ('a2222222-2222-2222-2222-222222222222', 101, '2025-04-17', -1200.00,'Landlord LLC','Rent',      3851.00, FALSE, 'April rent'),
  ('a3333333-3333-3333-3333-333333333333', 101, '2025-04-20', -15.25, 'Starbucks',   'Coffee',     NULL,    TRUE,  'Pending coffee');

-- 6a) Credit Card details
INSERT INTO credit_loan_details 
  (credit_id,              account_id, outstanding_balance, credit_limit,  apr,     minimum_payment, next_due_date, original_amount, maturity_date)
VALUES
  ('c1111111-1111-1111-1111-111111111111', 103,         500.00,              5000.00,       0.199,  25.00,          '2025-05-01',    NULL,            NULL);

-- 6b) Payment history on that card
INSERT INTO credit_payments 
  (payment_id, credit_id,                          payment_date, amount, status)
VALUES
  (1,          'c1111111-1111-1111-1111-111111111111','2025-03-01', 50.00,   'on-time'),
  (2,          'c1111111-1111-1111-1111-111111111111','2025-04-01', 25.00,   'on-time');

-- 7a) Investment account wrapper
INSERT INTO investment_accounts 
  (inv_account_id, account_id, account_type)
VALUES
  ('i1111111-1111-1111-1111-111111111111', 104, '401k');

-- 7b) Two holdings in that 401(k)
INSERT INTO investment_holdings 
  (holding_id, inv_account_id, asset_type, symbol, quantity, market_value, cost_basis, date_acquired)
VALUES
  (1,           'i1111111-1111-1111-1111-111111111111','stock','AAPL',10,   1600.00,      1250.00,     '2020-01-15'),
  (2,           'i1111111-1111-1111-1111-111111111111','ETF',  'VOO', 5,   2000.00,      1500.00,     '2019-06-20');

-- 7c) Investment transactions
INSERT INTO investment_transactions 
  (inv_tx_id,                           holding_id, tx_date,   tx_type, quantity, amount)
VALUES
  ('i_tx_1111-1111-1111-1111-111111111111', 1,          '2025-04-10','dividend',   0,       5.00),
  ('i_tx_2222-2222-2222-2222-222222222222', 1,          '2025-03-05','sell',       2,       350.00),
  ('i_tx_3333-3333-3333-3333-333333333333', 2,          '2025-02-20','buy',        5,       1500.00);
