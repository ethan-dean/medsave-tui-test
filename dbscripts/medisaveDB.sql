-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS medisave;

-- Use the database
USE medisave;

-- Create the users tableusers
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Replace 'medisave_user' and 'StrongPassword123!' with your desired username and password
CREATE USER IF NOT EXISTS 'medisave_user'@'localhost' IDENTIFIED BY 'Pass123!';

-- Grant the user permissions on the medisave database
GRANT SELECT, INSERT, UPDATE, DELETE ON medisave.* TO 'medisave_user'@'localhost';