-- Create database
CREATE DATABASE IF NOT EXISTS expenses;
USE expenses;

-- Create bills table with proper schema
CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO bills (name, amount, description) VALUES
('Alice', 125.50, 'Monthly electricity bill'),
('Bob', 80.00, 'Internet subscription'),
('Charlie', 45.75, 'Water bill'),
('Alice', 32.25, 'Groceries'),
('Bob', 15.50, 'Cleaning supplies');

-- Verify setup
SELECT 'Database setup completed successfully!' as status;
SELECT COUNT(*) as total_bills FROM bills;